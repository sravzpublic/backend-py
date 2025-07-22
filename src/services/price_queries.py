from src.services import mdb
from src.services.price_helpers.util import Util
from src.util import logger
from src.services.cache import Cache
from src.services import aws
from src.util import settings, helper
import pandas as pd
import numpy as np
import io

_logger = logger.RotatingLogger(__name__).getLogger()

class engine(object):
    """description of class"""

    def __init__(self):
        self.aws_engine = aws.engine()

    def get_historical_price(self, sravzid, src=settings.constants.S3_TARGET_AWS):
        '''
            from src.services.price_queries import engine
            pe = engine()
            pe.get_historical_price('stk_us_zoom')
        '''
        # collection_name = Util.get_hostorical_collection_name_from_sravz_id(sravzid)
        cache_key = 'get_historical_price_%s'%(sravzid)
        value = Cache.Instance().get(cache_key)
        if not value:
            if helper.is_user_asset(sravzid):
                value = aws.engine().download_object(settings.constants.AWS_USER_ASSETS_BUCKET, sravzid)
            else:
                # Override the src based on ticker type
                sources = settings.constants.PRICE_SRC_BY_SRAVZ_ID.get(helper.get_ticker_type(sravzid)) or [settings.constants.S3_TARGET_AWS]
                for _src in sources:
                    try:
                        if _src == settings.constants.S3_TARGET_AWS:
                            value = self.aws_engine.download_quotes_from_s3(sravzid)
                        elif _src in [settings.constants.S3_TARGET_CONTABO, settings.constants.S3_TARGET_IDRIVEE2]:
                            value = self.aws_engine.download_quotes_from_contabo(sravzid, target=_src)
                        # If price found at a source, break and use that price
                        if value:
                            break
                    except Exception:
                        _logger.error('Failed to fetch price for Sravz ID {0} at source {1}'.format(
                            sravzid, _src), exc_info=True)
        if value:
            Cache.Instance().add(cache_key, value)
        return value


    # Ensure the price is in assending order of price date
    def get_historical_price_df(self, sravzid, src='aws'):
        '''
            from src.services import price_queries
            se = price_queries.engine()
            gold = se.get_historical_price_df('fut_gold')
            platinum = se.get_historical_price_df('fut_platimum')
            us_ayi = se.get_historical_price_df('stk_us_ayi')
            [se.get_historical_price_df(sravz_id) for sravz_id in ["stk_us_ayi", "stk_us_axp", "stk_us_awk", "stk_us_azo", "stk_us_avb", "stk_us_avy", "stk_us_avg"]]
        '''
        historical_price = self.get_historical_price(sravzid, src=src)
        if not historical_price:
            _logger.info(f"Historical price data for sravz_id {sravzid} not found")
            return
        if helper.is_user_asset(sravzid):
            data_df = pd.read_csv(io.BytesIO(historical_price))
            return(self.format_df_for_frontend(data_df))
        else:
            # Convert the data from mongodb to df
            data = [{
                "Date" : row.get('Date') or row.get(b'Date'),
                "Volume" : row.get('Volume') or row.get(b'Volume'),
                "Last" : row.get('Last') or row.get(b'Last'),
                "OpenInterest" : row.get('OpenInterest') or row.get(b'OpenInterest'),
                "High" : row.get('High') or row.get(b'High'),
                "Low" : row.get('Low') or row.get(b'Low'),
                "Open" : row.get('Open') or row.get(b'Open'),
                "Change" : row.get('Change') or row.get(b'Change'),
                "Settle" : row.get('Settle') or row.get(b'Settle'),
                "AdjustedClose" : row.get('AdjustedClose') or row.get(b'AdjustedClose'),
            } for row in historical_price]
            data_df = self.get_df_from_price_data(data)
            data_df = data_df.replace(0, np.nan)
            data_df = data_df.ffill()
            # Sort price by assending
            data_df = data_df.sort_index(ascending=True)
        return data_df


    # Ensure the price is in assending order of price date
    def get_historical_hash_rate_df(self, sravzid):
        '''
        '''
        historical_price = self.get_historical_price(sravzid)
        if helper.is_user_asset(sravzid):
            data_df = pd.read_csv(io.BytesIO(historical_price))
            return(self.format_df_for_frontend(data_df))
        else:
            data = [{
                "Date" : row.get('Date') or row.get(b'Date'),
                "HashRateGH" : row.get('HashRateGH') or row.get(b'HashRateGH'),
            } for row in historical_price]
            data_df = self.get_df_from_price_data(data)
            data_df = data_df.replace(0, np.nan)
            data_df = data_df.ffill()
            data_df = data_df.sort_values('Date')
        return data_df

    def get_df_from_price_data(self, data, from_date = None):
        '''
            Returns data from from List of price data dicts
            from src.services import price_queries
            se = price_queries.engine()
            data = se.get_historical_price_df('fut_platimum_feb_17_usd_lme')
            se.get_df_from_price_data(data, from_date = None)
        '''
        data_df = pd.DataFrame(data)
        return self.format_df_for_frontend(data_df)

    def format_df_for_frontend(self, data_df, from_date = None):
        '''
            Returns df which can be used by the UI:
            "{\"columns\":[\"Changefut_gold\",\"Highfut_gold\",\"Lastfut_gold\",\"Lowfut_gold\",
                           \"Openfut_gold\",\"OpenInterestfut_gold\",\"Settlefut_gold\",\"Volumefut_gold\"],
             \"index\": [\"1974-12-31 00:00:00\",\"1975-01-02 00:00:00\",\"1975-01-03 00:00:00\"],
             \"data\":[[null,191.5,183.9,182.7,191.0,null,183.9,512.0]]}"
            se = price_queries.engine()
            data = se.get_historical_price_df('fut_platimum_feb_17_usd_lme')
            se.get_df_from_price_data(data, from_date = None)
        '''
        if not data_df.empty:
            if 'Date' not in data_df.index.names:
                data_df.set_index(["Date"], inplace = True)
            data_df = data_df.sort_index()
            # Drops complete data frame
            #data_df.dropna(inplace = True)
            if from_date:
                data_df = data_df[from_date:]
        return data_df

    # Get a generic df from s3
    def get_df_from_s3(self, sravzid):
        '''
            from src.services.price_queries import engine
            pe = engine()
            pe.get_df_from_s3('data_undefined_nike_srbounce_v2_list_of_trades_2022-11-26.csv_1669569679677')
        '''
        historical_price = self.get_historical_price(sravzid)
        data_df = pd.read_csv(io.BytesIO(historical_price))
        return data_df


