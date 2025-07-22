'''
    Performs spread analysis
'''
from src.analytics import pca
from src.util import logger, aws_cache, settings, helper
from src.services import mdb
# from dask.distribsuted import Client
import pandas as pd
import json
LOGGER = logger.RotatingLogger(__name__).getLogger()


def get_stat_for_ticker(ticker, upload_to_s3 = True):
    e = pca.engine()
    awse = aws_cache.engine()
    helper.empty_cache_if_new_day()
    try:
        LOGGER.info("processing %s" % (ticker))
        sravz_id = ticker['SravzId']
        asset_name = ticker['Name']
        df_price = e.get_price_data_dfs([sravz_id])
        describe_df = df_price.describe().round(3)
        describe_df = describe_df.rename(columns={'AdjustedClose': sravz_id}).transpose().loc[[sravz_id]]
        describe_df['SravzId'] = sravz_id
        describe_df['FromDate'] = df_price.iloc[[1]].index
        describe_df['ToDate'] = df_price.iloc[[-1]].index
        describe_df['AdjustedClose'] = df_price.iloc[[-1]]['AdjustedClose'][0]
        try:
            describe_df['AdjustedCloseVsMaxPercent'] = (describe_df['AdjustedClose'] - describe_df['max'])/describe_df['max']*100
            describe_df['AdjustedCloseVsMeanPercent'] = (describe_df['AdjustedClose'] - describe_df['mean'])/describe_df['mean']*100
            describe_df['AdjustedCloseVsMinPercent'] = (describe_df['AdjustedClose'] - describe_df['min'])/describe_df['min']*100
            describe_df = describe_df.round({'AdjustedCloseVsMaxPercent': 3, 'AdjustedCloseVsMeanPercent': 3, 'AdjustedCloseVsMinPercent': 3})
        except Exception:
            LOGGER.exception(f"Unable to calculate prices")
        describe_df['Name'] = asset_name
        return describe_df
    except Exception as e:
        LOGGER.error('Failed to process ticker {0}'.format(ticker), exc_info=True)
    return None


def get_stats(tickers, upload_to_s3 = True):
    mdbe = mdb.engine()
    tickers = tickers or mdbe.get_collection_items(settings.constants.FUTURE_ASSETS_COLLECTION)
    for ticker in tickers:
        try:
            LOGGER.info("processing %s" % (ticker))
            get_stat_for_ticker(ticker)
        except Exception as e:
            LOGGER.error('Failed to process ticker {0}'.format(ticker), exc_info=True)



def get_data(tickers):
    '''
        Uploads futures statistics
    '''
    awse = aws_cache.engine()
    mdbe = mdb.engine()
    tickers = tickers or mdbe.get_collection_items(settings.constants.FUTURE_ASSETS_COLLECTION)
    dfs = [get_stat_for_ticker(ticker) for ticker in tickers]
    df_all = pd.concat(dfs)
    # Data is the second parameter!!!
    awse.upload_data_to_contabo(settings.constants.CONTABO_BUCKET,    
    json.dumps(df_all.to_dict('records'), cls=helper.DatesEncoder),
    f"{settings.constants.CONTABO_BUCKET_PREFIX}/price_stats/all.json")

if __name__ == '__main__':
    # get_stats([{'SravzId': 'fut_us_6a'}, {'SravzId': 'fut_us_gc'}])
    # get_data([{'SravzId': 'fut_us_6a', 'Name': 'Australian Dollar Futures'}, {'SravzId': 'fut_us_gc', 'Name': 'Gold'}])
    # print(get_stat_for_ticker({'SravzId': 'fut_us_gc', 'Name': 'Gold'}))
    get_data(None)

