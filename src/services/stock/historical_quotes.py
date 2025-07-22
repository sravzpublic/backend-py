from src.util import logger, helper, settings
from src.services import mdb, aws
import datetime, pymongo
from src.services.quotes_providers.quote import engine as quote_engine
import urllib.request, json
from src.services.assets import indices
# from dask.distributed import Client

LOGGER = logger.RotatingLogger(__name__).getLogger()

def upload_ticker(ticker, upload_to_db = True):
    awse = aws.engine()
    collection_name = helper.get_generic_sravz_id("stk_us_%s"%(ticker))
    LOGGER.info(f"Uploading to collection {collection_name}")
    try:
        if awse.is_quote_updated_today(collection_name):
            return (ticker, False)        
        url = "https://eodhistoricaldata.com/api/eod/{0}.US?api_token={1}&order=d&fmt=json".format(ticker, settings.constants.EODHISTORICALDATA_API_KEY2)
        LOGGER.info("Processing ticker %s" % (ticker))
        json_data = urllib.request.urlopen(url).read()
        data  = json.loads(json_data)
        quotes = []
        for quote in data:
            quote['Date'] = datetime.datetime.strptime(quote.pop('date'), '%Y-%m-%d')
            quote["Volume"] = quote.pop("volume")
            quote["Open"] = quote.pop("open")
            quote["High"] = quote.pop("high")
            quote["Low"] = quote.pop("low")
            quote["Close"] = quote.pop("close")
            quote["AdjustedClose"] = quote.pop("adjusted_close")
            quotes.append(quote)
        if upload_to_db and quotes:
            LOGGER.info(f"Uploading {len(quotes)} quotes to collection {collection_name}")
            awse.upload_quotes_to_contabo(quotes, collection_name)
            awse.upload_quotes_to_contabo(quotes, collection_name, target=settings.constants.S3_TARGET_IDRIVEE2)
            return (ticker, True)
    except Exception:
        LOGGER.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
    return (ticker, False)


class engine(object):
    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        _quote_engine = quote_engine()
        self.awse = aws.engine()
        self.source_map = {
            0: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_STOOQ),
            1: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_INVESTOPEDIA),
            2: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_MACROTRENDS),
            3: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_WSJ),
            4: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_TIINGO),
            5: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_ALPHA_ADVANTAGE),
            6: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_YAHOO),
            7: lambda tickers: _quote_engine.get_historical_price(tickers, settings.constants.EODHISTORICALDATA)
        }
        self.num_sources = self.max_retires = len(self.source_map)

    def chunk(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def upload_quotes(self, upload_to_db = False, tickers = []):
        tickers_temp = tickers
        source_index = list(range(self.num_sources))
        result = {}
        failed_tickers = []
        found_tickers = []
        count = 0
        while (count < self.max_retires):
            self.logger.info("Processing loop %s"%(count))
            chunks = self.chunk(tickers_temp, self.num_sources)
            for idx, chunk in enumerate(chunks):
                #shuffle(source_index)
                source_id = source_index[idx%len(source_index)] #if idx < len(source_index) else 0
                source = self.source_map.get(source_id)
                self.logger.info("Processing chunk %s using source %s"%(idx, source_id))
                result[idx] = source(tickers = chunk)
                if upload_to_db:
                    [self.upload_historical_quotes_data_to_db(ticker_data['ticker'], ticker_data['data']) for ticker_data in result[idx].tickers_result]
                    # Delete data to save memory
                    result[idx].tickers_result = None
            for quote_value in list(result.values()):
                failed_tickers.extend(quote_value.failed_tickers)
                found_tickers.extend(quote_value.passed_tickers)
            if failed_tickers:
                count = count + 1
                tickers_temp = list(set(failed_tickers))
                self.logger.info("Failed tickers in this loop %s: %s"%(count, str(tickers_temp)))
        missing_tickers = list(set(tickers) - set(found_tickers))
        extra_tickers = list(set(found_tickers) - set(tickers))
        self.logger.info("These are missing tickers: Count: %s: %s"%(len(missing_tickers), str(missing_tickers)))
        self.logger.info("These are extra tickers: Count: %s: %s"%(len(extra_tickers), str(extra_tickers)))

    def get_historical_us_index_components_quotes(self, upload_to_db = False, tickers = []):
        '''
            e = engine()
            #e.get_snp_quotes(upload_to_db = False)
            e.get_snp_quotes(upload_to_db = True)
        '''
        e = mdb.engine()
        tickers = tickers or [item['ticker'] for item in e.get_collection_items_fields(settings.constants.RUSSELL_COMPONENTS_COLLECTION_NAME, sortDirection = pymongo.ASCENDING,
        field_clause = {'ticker': 1, '_id': 0})] + [item['ticker'] for item in e.get_collection_items_fields(settings.constants.SPX_COMPONENTS_COLLECTION_NAME,
        sortDirection = pymongo.ASCENDING, field_clause = {'ticker': 1, '_id': 0})]
        tickers = (list(set(tickers)))
        self.upload_quotes(upload_to_db=upload_to_db, tickers=tickers)

    def get_historical_russell_3000_quotes(self, upload_to_db = False, tickers = []):
        e = mdb.engine()
        tickers = tickers or [item['ticker'] for item in e.get_collection_items_fields(settings.constants.RUSSELL_COMPONENTS_COLLECTION_NAME, sortDirection = pymongo.ASCENDING, field_clause = {'ticker': 1, '_id': 0})]
        self.upload_quotes(upload_to_db=upload_to_db, tickers=tickers)


    def get_historical_snp_quotes(self, upload_to_db = False, tickers = []):
        '''
            e = engine()
            #e.get_snp_quotes(upload_to_db = False)
            e.get_snp_quotes(upload_to_db = True)
        '''
        e = mdb.engine()
        tickers = tickers or [item['ticker'] for item in e.get_collection_items_fields(settings.constants.SPX_COMPONENTS_COLLECTION_NAME, sortDirection = pymongo.ASCENDING, field_clause = {'ticker': 1, '_id': 0})]
        self.upload_quotes(upload_to_db=upload_to_db, tickers=tickers)


    def upload_historical_quotes_data_to_db(self, ticker, data):
        if not data:
            self.logger.warn("Historical quote data not found for ticker {0}".format(ticker))
        else:
            mdbe_historical = mdb.engine(database_name='historical', database_url='historical_url')
            collection_name = helper.get_generic_sravz_id("stk_us_%s"%(ticker))
            c_quotes_col = mdbe_historical.get_collection(collection_name)
            mdbe_historical.create_unique_index_collection([ ("Date", pymongo.ASCENDING)], collection_name, key_name= 'date_unique_index')
            for row in data:
                if 'Date' in row:
                    historical_data = {
                        "Date" : datetime.datetime.strptime(row.get('Date'), '%Y-%m-%d'),
                        "Volume" : helper.util.getfloat(row.get("Volume")),
                        "High" : helper.util.getfloat(row.get("High")),
                        "Last" : helper.util.getfloat(row.get("Close")),
                        "Low" : helper.util.getfloat(row.get("Low")),
                        "Open" : helper.util.getfloat(row.get("Open"))
                    }
                    c_quotes_col.update_one({"Date": historical_data['Date']}, {"$set": historical_data}, upsert=True)

    def upload_quotes_to_db(self, data, collection_name, ndays_back=None):
        mdbe_historical = mdb.engine(
            database_name='historical', database_url='historical_url')
        quotes_col = mdbe_historical.get_collection(collection_name)
        for item in data:
            if ndays_back and (datetime.datetime.now() - item['Date']).days > ndays_back:
                continue
            quotes_col.update_one({"Date": item['Date']}, {
                "$set": item}, upsert=True)

    def get_eodhistoricaldata_historical_stock_quotes(self, tickers = [], upload_to_db = True, ndays_back=None):
        '''
            https://eodhistoricaldata.com/api/eod/AEDAUD.US?api_token={1}&order=d&fmt=json
            Uploads RUSSELL 3000 components

            from src.services.stock.historical_quotes import engine
            e = engine()
            e.get_eodhistoricaldata_historical_stock_quotes()
        '''
        tickers = self.get_tickers(tickers=tickers)
        [upload_ticker(ticker) for ticker in tickers]


    def get_tickers(self, tickers=[]):
        if tickers:
            return tickers
        tickers_map = {}
        for index in settings.constants.INDEX_COMPONENTS_QUOTES_TO_UPLOAD:
            [tickers_map.update({x['Code']: x}) for x in json.loads(indices.get_index_components_from_s3(index))['Components'].values()]
        tickers = list(tickers_map.keys())
        tickers = (list(set(tickers)))
        return tickers

if __name__ == '__main__':
    e = engine()
    e.get_eodhistoricaldata_historical_stock_quotes()



