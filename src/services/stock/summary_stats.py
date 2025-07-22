from src.util import logger, settings, helper
from src.services import aws
import datetime
import json, os
from src.services.assets import indices
# from dask.distributed import Client
import pandas as pd
from src.analytics import pca, tears
from dateutil.relativedelta import relativedelta
import awswrangler as wr
import urllib.request, json
from src.services import price_queries

LOGGER = logger.RotatingLogger(__name__).getLogger()

def get_stats_df(ticker):
    '''
        Uploads dataframe summary stats and pyfolio stats to contabo
    '''
    try:
        pqe = price_queries.engine()
        pcae = pca.engine()
        awse = aws.engine()
        helper.empty_cache_if_new_day()
        upload_summary_stats_df(ticker, pqe, awse)
        upload_pyfolio_stats_df(ticker, pcae, awse)
        return (True, ticker)
    except Exception:
        LOGGER.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
    return (False, ticker)

def upload_pyfolio_stats_df(ticker, pcae:pca.engine,  awse: aws.engine):
    benchmark_rets = pcae.get_percent_daily_returns(['idx_us_gspc']).tz_localize(None)
    number_of_years_back = 10
    benchmark_rets = benchmark_rets[benchmark_rets.index > datetime.datetime.now() - relativedelta(years=number_of_years_back)]
        # Calculate pyfolio 
    stock_rets = pcae.get_percent_daily_returns([ticker], src='contabo').tz_localize(None)
    stock_rets = stock_rets[stock_rets.index > (datetime.datetime.now() - relativedelta(years=number_of_years_back))]
    df = tears.get_perf_stats(stock_rets.squeeze(), benchmark_rets=benchmark_rets.squeeze(), bootstrap=False, sravzid=ticker)
        # convert dataframe to json string
    df_dict = df.to_dict(orient='records')
    collection_name = f"{ticker}_stats"
    awse.upload_quotes_to_contabo(df_dict, collection_name)

def upload_summary_stats_df(ticker: str, pqe: price_queries.engine, awse: aws.engine):
    '''
        Uploads summary stats change over max price, min price, mean price etc
    '''
    price_df = pqe.get_historical_price_df(ticker, src='contabo')
    # Calcualate summary
    # Get summary statistics
    summary_stats = price_df['AdjustedClose'].describe()
    # Get latest price (last row) 
    latest_row = price_df.iloc[-1]
    latest_price = latest_row['AdjustedClose']
    percentage_over_max = ((latest_price - summary_stats["max"]) / summary_stats["max"]) * 100
    percentage_over_min = ((latest_price - summary_stats["min"]) / summary_stats["min"]) * 100
    percentage_over_mean = ((latest_price - summary_stats["mean"]) / summary_stats["mean"]) * 100    
    summary_stats["percentage_over_max"] = round(percentage_over_max, 2)        
    summary_stats["percentage_over_min"] = round(percentage_over_min, 2)        
    summary_stats["percentage_over_mean"] = round(percentage_over_mean, 2)        
    summary_stats_df_dict = summary_stats.to_dict()
    summary_stats_df_dict.update({
            "latest_price": latest_price,
            "earliest_price": price_df.iloc[0]["AdjustedClose"],
            "earliest_timestamp": price_df.index[0].isoformat(),            
            "latest_timestamp": price_df.index[-1].isoformat(),
        })
    summary_stats_collection_name = f"{ticker}_summary_stats"
    # As to be an array of dict
    awse.upload_quotes_to_contabo([summary_stats_df_dict], summary_stats_collection_name)

def upload_quotes_stats_df_to_s3(df, s3_file_name="quotes_stats"):
    awse = aws.engine()    
    path = f"s3://{settings.constants.SRAVZ_DATA_S3_BUCKET}/{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{s3_file_name}.parquet"
    wr.s3.to_parquet(df, path)    
    local_path = f"/tmp/{s3_file_name}.parquet"
    df.to_parquet(local_path, index=False)
    awse.upload_file_to_contabo(settings.constants.SRAVZ_DATA_S3_BUCKET, f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{s3_file_name}.parquet", local_path)
    LOGGER.info(f"Uploaded {len(df)} records to s3 in parquet format at {path}")

class engine(object):
    STATS_SUFFIX = "_stats"
    SUMMARY_STATS_SUFFIX = "_summary_stats"
    STATS_TARGET_S3 = "quotes_stats"
    SUMMARY_STATS_TARGET_S3 = "quotes_summary_stats"

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    def get_fundamental(self, ticker_code):
        try:
            awse = aws.engine()
            helper.empty_cache_if_new_day()
            ticker, code = ticker_code
            collection_name = f"{ticker}_fundamental"
            url = "https://eodhistoricaldata.com/api/fundamentals/{0}?api_token={1}&order=d&fmt=json".format(code, settings.constants.EODHISTORICALDATA_API_KEY)
            json_data = urllib.request.urlopen(url).read()
            data  = json.loads(json_data)
            awse.upload_quotes_to_contabo(data, collection_name)
            return (True, ticker)
        except Exception:
            LOGGER.error('Failed to process fundamental for ticker {0}'.format(ticker), exc_info=True)
        return (False, ticker)

    def get_fundamentals(self, tickers = []):
        '''
            tickers = [(sravz_id, code)]
            from src.services.stock.summary_stats import engine
            e = engine()
            e.get_fundamentals(tickers=[('stk_us_adbe','ADBE')])
        '''
        awse = aws.engine()
        tickers_map = {}
        for index in settings.constants.INDEX_COMPONENTS_QUOTES_TO_UPLOAD:
            [tickers_map.update({x['Code']: x}) for x in json.loads(indices.get_index_components_from_s3(index))['Components'].values()]
        # Update the ticker format to stk_us_abbv 
        tickers = tickers or [(f"stk_us_{ticker.lower()}", ticker) for ticker in list(tickers_map.keys())]
        tickers = (list(set(tickers)))
        return [self.get_fundamental(ticker) for ticker in tickers]

    def get_summary_stats(self, tickers = []):
        '''
            https://eodhistoricaldata.com/api/eod/AEDAUD.US?api_token={1}&order=d&fmt=json
            Uploads RUSSELL 3000 components

            from src.services.stock.historical_quotes import engine
            e = engine()
            e.get_eodhistoricaldata_historical_stock_quotes()
        '''
        if not tickers:
            tickers_map = {}            
            for index in settings.constants.INDEX_COMPONENTS_QUOTES_TO_UPLOAD:
                [tickers_map.update({x['Code']: x}) for x in json.loads(indices.get_index_components_from_s3(index))['Components'].values()]
            # Update the ticker format to stk_us_abbv 
            tickers = [f"stk_us_{ticker.lower()}" for ticker in list(tickers_map.keys())]
        tickers = (list(set(tickers)))
        return [get_stats_df(ticker) for ticker in tickers]

    def get_all_tickers(self):
        tickers_map = {}    
        for index in settings.constants.INDEX_COMPONENTS_QUOTES_TO_UPLOAD:
            [tickers_map.update({x['Code']: x}) for x in json.loads(indices.get_index_components_from_s3(index))['Components'].values()]
        # Update the ticker format to stk_us_abbv         
        return [f"stk_us_{ticker.lower()}" for ticker in list(tickers_map.keys()) if ticker]

    def get_all_fundamental_tickers(self):
        tickers_map = {}    
        for index in settings.constants.INDEX_COMPONENTS_QUOTES_TO_UPLOAD:
            [tickers_map.update({x['Code']: x}) for x in json.loads(indices.get_index_components_from_s3(index))['Components'].values()]
        # Update the ticker format to stk_us_abbv 
        return [(f"stk_us_{ticker.lower()}", ticker) for ticker in list(tickers_map.keys()) if ticker]

    def upload_final_stats_df(self, tickers = []):
        '''
            from src.services.stock import summary_stats
            summary_engine = summary_stats.engine()
            summary_engine.upload_final_stats_df()        
        '''
        # Update the ticker format to stk_us_abbv 
        tickers = tickers or self.get_all_tickers()
        tickers = (list(set(tickers)))
        # Load clamar ratio etc - pyfolio stats
        self.upload_all_stats_df(tickers, self.STATS_SUFFIX, self.STATS_TARGET_S3)
        # Load max to current price, min, mean etc - summary stats
        self.upload_all_stats_df(tickers, self.SUMMARY_STATS_SUFFIX, self.SUMMARY_STATS_TARGET_S3)

    def upload_all_stats_df(self, tickers, source_s3_file_name, target_s3_file_name):
        all_dfs = []    
        awse = aws.engine()                
        for ticker in tickers:
            collection_name = f"{ticker}{source_s3_file_name}"
            try:
                df = pd.DataFrame(awse.download_quotes_from_contabo(collection_name))
                df['sravz_id'] = ticker
                all_dfs.append(df)
            except:
                self.logger.exception("Summary stat for %s not found - collection_name: %s", ticker, collection_name)
        if all_dfs:
            df_all = pd.concat(all_dfs)
            # df_all.reset_index(level=0, inplace=True)
            # df_all = df_all.rename(columns={'index': 'sravz_id'})
            df_all.columns = [x.lower() for x in df_all.columns]
            df_all.columns = [x.replace(" ", "_").replace("%", "_pct") for x in df_all.columns]
            df_all = df_all.round(4)
            upload_quotes_stats_df_to_s3(df_all, target_s3_file_name)
        else:
            self.logger.error("No stats found")

    def get_quotes_stats_df(df, s3_file_name="quotes_stats", src = 'contabo'):
        awse = aws.engine()    
        path = f"s3://{settings.constants.SRAVZ_DATA_S3_BUCKET}/{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{s3_file_name}.parquet"
        if src == 'contabo':        
            awse.download_file_from_s3(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                                    f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{s3_file_name}.parquet", 
                                    f"/tmp/{s3_file_name}.parquet", 
                                    target=settings.constants.S3_TARGET_CONTABO)
            return pd.read_parquet(f"/tmp/{s3_file_name}.parquet")
        elif src == 'aws':
            return wr.s3.read_parquet(path)    
        raise Exception(f"Unsupported src: {src}")

if __name__ == '__main__':
    #e = engine()
    # ['stk_us_zoom', 'stk_us_mmm']
    #e.get_summary_stats()
    pass



