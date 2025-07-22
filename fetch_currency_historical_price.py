#!/usr/bin/env python
from services import price, aws
from util import settings
from datetime import datetime
import json


def get_price(asset_name = 'fut_XAU/USD_NA_NA_usd_cme'):
    price_engine = price.engine()
    return price_engine.get_historical_price(asset_name, asset_type = settings.constants.CURRENCY)
    
def transfrom_price(asset_name = 'fut_XAU/USD_NA_NA_usd_cme'):
    """ fut_XAU/USD_NA_NA_usd_cme
        Input: 
        [
         [u':', u'Updated: 05/12/16 21:30'],
         [],
         [u'Sunday  4 December 2016', u'XAU/USD', u'1180.31500', u'XAU USD rate for Sunday  4 December 2016'],
         [u'Saturday  3 December 2016', u'XAU/USD', u'1177.00000', u'XAU USD rate for Saturday  3 December 2016']
        ]    
        Output:
        [
         [datetime.datetime(2016, 12, 4, 0, 0), u'1180.31500'], [datetime.datetime(2016, 12, 3, 0, 0), u'1177.00000'],
        ]
    """
    if asset_name == 'fut_XAU/USD_NA_NA_usd_cme':
        data = get_price(asset_name)[2:]
        for x in data:
            try:
                x[0] = datetime.strptime(x[0], '%A %d %B %Y').strftime("%m%d%Y")
            except:
                pass
        data = [[data[0], data[2]] for data in data]
        return data

def upload_price(asset_name = 'fut_XAU/USD_NA_NA_usd_cme'):
    data = transfrom_price(asset_name)
    awse = aws.engine()
    awse.upload_to_bucket(settings.constants.DEFAULT_BUCKET_NAME, settings.constants.get_default_price_key(asset_name) , json.dumps(data).encode())

if __name__ == '__main__':
    upload_price('fut_XAU/USD_NA_NA_usd_cme')
    
