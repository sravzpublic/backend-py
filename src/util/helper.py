'''
Created on Jan 20, 2017

@author: admin
'''
import os, matplotlib
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from decorator import decorator
from src.util import logger, aws_cache
from src.services.cache import Cache
from . import settings
from dateutil import parser
import hashlib
import json
import numpy as np
import pandas as pd
import uuid
import matplotlib.pyplot as plt
from titlecase import titlecase
import datetime
import re

LOGGER = logger.RotatingLogger(__name__).getLogger()


class DatesEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(obj, datetime.datetime):
            return obj.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(obj, pd.core.frame.DataFrame):
            return obj.to_json(orient='split')
        elif isinstance(obj, bytes):
            return obj.encode()
        return super(DatesEncoder, self).default(obj)


class DatesDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        type = obj['_type']
        if type == 'datetime':
            return parser.parse(obj['value'])
        return obj


def convert(data):
    '''
        Convert all binary data to strings
    '''
    if isinstance(data, bytes):
        return data.decode()
    if isinstance(data, (str, int, float)):
        return str(data)
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return tuple(map(convert, data))
    if isinstance(data, list):
        return list(map(convert, data))
    if isinstance(data, set):
        return set(map(convert, data))


def get_generic_sravz_id(SravzId):
    '''
        Futures roll, hence get generic ID if future, remove roll date
        Not used anymore since SravzID by default uses generic ID
    '''
    SravzId = convert(SravzId)
    #generic_id = "_".join(SravzId.split(
    #    "_")[0:2]) if "fut" in SravzId else SravzId
    return SravzId.lower()


def is_user_asset(SravzId):
    '''
        Return True if User Asset else False if Sravz Asset
        User Assets are stored in S3/DynamoDB, Sravz Assets are stored in MongoDB
    '''
    SravzId = convert(SravzId)
    # return len(SravzId.split("_")[0]) > settings.constants.SRAVZ_ASSET_PREFIX_LEN
    # greater/equal timestamp length: 1555619488953
    return SravzId.split("_")[-1].isdigit() and len(SravzId.split("_")[-1]) >= 13


def get_ticker_type(SravzId):
    '''
        Return the ticker type:
    '''
    if settings.constants.TICKER_TYPE_STOCK in SravzId:
        return settings.constants.TICKER_TYPE_STOCK
    elif settings.constants.TICKER_TYPE_FUTURE in SravzId:
        return settings.constants.TICKER_TYPE_FUTURE
    elif settings.constants.TICKER_TYPE_MUTUAL_FUND in SravzId:
        return settings.constants.TICKER_TYPE_MUTUAL_FUND    
    elif settings.constants.TICKER_TYPE_ETF in SravzId:
        return settings.constants.TICKER_TYPE_ETF   
    return None


def get_stock_ticker_from_sravz_id(SravzId):
    '''
        Get the ticker from the sravz_id
        for stk_us_FB return FB
    '''
    SravzId = convert(SravzId)
    ticker = SravzId.split("_")[2] if "stk" in SravzId else SravzId
    return ticker.lower()


def empty_cache_if_new_day():
    key = 'last_cache_empty_date'
    try:
        value = Cache.Instance().get(key)
        if not value or (datetime.datetime.today() - value).days > 0:
            Cache.Instance().remove_all()
            Cache.Instance().add(key, datetime.datetime.today())
            LOGGER.info(
                "Cache emptied. Last cache empty date: {0}".format(value))
        else:
            LOGGER.info(
                "Cache not emptied. Last cache empty date in cache: {0}".format(value))
    except:
        LOGGER.exception("Error empty cache or set last_cache_empty_date")


def get_md5_of_string(value):
    return hashlib.md5(value.encode()).hexdigest()


def get_price_column_to_use_for_the_asset(sravzid, price_df, change_cols_to_titlecase = True):
    if change_cols_to_titlecase:
        price_df.columns = [titlecase(x) for x in price_df.columns]
    if 'Settle' in  price_df.columns and not price_df['Settle'].isnull().values.any():
        return 'Settle'
    elif 'Last' in  price_df.columns and not price_df['Last'].isnull().values.any():
        return 'Last'
    elif (change_cols_to_titlecase and 'Adjustedclose' in  price_df.columns) and not price_df['Adjustedclose'].isnull().values.any():
        return 'Adjustedclose'
    elif 'AdjustedClose' in  price_df.columns and not price_df['AdjustedClose'].isnull().values.any():
        return 'AdjustedClose'
    elif 'Close' in price_df.columns and not price_df['Close'].isnull().values.any():
        return 'Close'
    raise ValueError('Did not find Settle, Last, AdjustedClose or Close column in the price df')



def save_plt(fig, file_path_to_use = None):
    file_path = file_path_to_use or '/tmp/{0}'.format(uuid.uuid4().hex)
    fig.savefig(file_path)
    plt.close(fig)
    return "{0}.png".format(file_path)

@decorator
def save_plot_to_file(func, *args, **kwargs):
    fig = func(*args, **kwargs)
    # TODO: Find way to add footer
    # fig.suptitle('As of %s'%(datetime.datetime.now().strftime("%m/%d/%Y")))
    return save_plt(fig)

@decorator
def empty_cache(func, *args, **kwargs):
    empty_cache_if_new_day()
    return func(*args, **kwargs)

@decorator
def save_file_to_contabo(func, *args, **kwargs):
    fig,bucket_key = func(*args, **kwargs)
    local_saved_file_path = save_plt(fig)
    aws_cache_engine = aws_cache.engine()
    aws_cache_engine.upload_file_to_contabo(settings.constants.CONTABO_BUCKET, bucket_key, local_saved_file_path)

@decorator
def save_data_to_contabo(func, *args, **kwargs):
    args_,kwargs = func(*args, **kwargs)
    bucket_key = args_[1]
    aws_cache_engine = aws_cache.engine()
    args = [settings.constants.CONTABO_BUCKET, *args_]
    aws_cache_engine.upload_data_to_contabo(*args, **kwargs)
    return {'bucket_name': "",
    'key_name': "",
    'data': None,
    'signed_url': f'https://usc1.contabostorage.com/adc59f4bb6a74373a1ebd286a7b11b60:sravz/{settings.constants.CONTABO_BUCKET}/{bucket_key}'}

def concat_images(imga, imgb):
    """
    Combines two color image ndarrays side-by-side.
    """
    ha,wa = imga.shape[:2]
    hb,wb = imgb.shape[:2]
    total_height = ha +  hb
    max_width = np.max([wa, wb])
    new_img = np.zeros(shape=(total_height, max_width, 3))
    new_img[:ha,:wa]=imga
    new_img[ha:ha+hb,:wb]=imgb
    return new_img

@decorator
def concat_n_images(func, *args, **kwargs):
    """
    Combines N color images from a list of image paths.
    """
    image_path_list = func(*args, **kwargs)
    img_path = '/tmp/{0}.png'.format(uuid.uuid4().hex)
    output = None
    for i, img_path in enumerate(image_path_list):
        img = plt.imread(img_path)[:,:,:3]
        if i==0:
            output = img
        else:
            output = concat_images(output, img)
    plt.imsave(img_path, output)
    return img_path

def get_list_part_based_on_day(data):
    # Calculate the current day of the month
    current_day = datetime.datetime.now().day
    # Calculate the index of the part corresponding to the current day
    # Subtract 1 to make it 0-indexed
    index = (current_day - 1) % settings.constants.MUTUAL_FUNDS_FUNDAMENTAL_DATA_DAYS_BEFORE_UPDATE
    # Return the part of the list based on the index
    part_size = len(data) // settings.constants.MUTUAL_FUNDS_FUNDAMENTAL_DATA_DAYS_BEFORE_UPDATE
    return data[index * part_size : (index + 1) * part_size]

class util(object):
    '''
    Helper methods
    '''

    def __init__(self, params):
        '''

        '''
    @staticmethod
    def get_n_years_back_date(n_years):
        return (datetime.datetime.now() - datetime.timedelta(days=n_years*365)).strftime("%Y-%m-%d")

    @staticmethod
    def get_n_days_back_date(n_days):
        return (datetime.datetime.now() - datetime.timedelta(days=n_days)).strftime("%Y-%m-%d")

    @staticmethod
    def getfloat(value):
        if value and isinstance(value, str):
            # value = value.replace(',', '')
            # decimal_point_char = locale.localeconv()['decimal_point']
            value = re.findall(r"[-+]?\d*\.\d+|\d+", value).pop()
        try:
            v = float(value)
            return v
        except:
            return 0.0

    @staticmethod
    def getint(value):
        try:
            v = int(value)
            return v
        except:
            return 0

    @staticmethod
    def translate_string_to_number(in_string):
        '''
            #Futures roll, hence get generic ID if future, remove roll date
            from src.util import helper
            helper.util.translate_string_to_number("$10")
        '''
        # Did not work in vagrant
        # return in_string.translate(None, ',$')
        if isinstance(in_string, str):
            return in_string.replace(",", "").replace('$', "")
        return in_string

    @staticmethod
    def get_tempfile_path(fileName):
        return os.path.join(settings.constants.get_cache_config()['dir'],
                            "{0}_{1}".format(fileName, datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))

    @staticmethod
    def get_temp_file():
        return '/tmp/{0}'.format(uuid.uuid4().hex)

    @staticmethod
    def convert_columns_and_index_to_str(df):
        cols_str = [column.decode('utf-8') for column in df.columns if isinstance(column, bytes)]
        if cols_str:
            df.columns = cols_str
        #df.index = [index.decode('utf-8') for index in df.index if isinstance(index, bytes)]
        return df
