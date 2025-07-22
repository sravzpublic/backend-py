import datetime, pymongo, urllib.request, json
from src.util import settings, helper, logger
from src.services import webcrawler, aws
from src.services import mdb, quotes_providers
from src.services.quotes_providers import yahoo



class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    # def upload_quotes_to_s3(self, data, collection_name):
    #     # mdbe_historical = mdb.engine(
    #     #     database_name='historical', database_url='historical_url')
    #     # quotes_col = mdbe_historical.get_collection(collection_name)
    #     # Upload quotes to s3
    #     self.awse.upload_to_bucket(settings.constants.SRAVZ_DATA_S3_BUCKET,
    #     f"{settings.constants.SRAVZ_HISTORICAL_DATA_PREFIX}/{collection_name}.json",
    #     json.dumps(data, default=default), gzip_data=True)
    #     # for item in data:
    #     #     if ndays_back and (datetime.datetime.now() - item['Date']).days > ndays_back:
    #     #         continue
    #     #     quotes_col.update_one({"Date": item['Date']}, {
    #     #         "$set": item}, upsert=True)

    def get_eodhistoricaldata_historical_index_quotes(self, tickers = [], upload_to_db = False, ndays_back=None):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.INDEX_ASSETS_COLLECTION)
        for ticker in [ticker for ticker in tickers if not self.awse.is_quote_updated_today(ticker['SravzId'])]:
            try:
                url = "https://eodhistoricaldata.com/api/eod/{0}.INDX?api_token={1}&order=d&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
                self.logger.info("processing %s" % (url))
                json_data = urllib.request.urlopen(url).read()
                data  = json.loads(json_data)
                ticker.pop('_id')
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
                if upload_to_db:
                    self.logger.info("Uploading %s quotes to s3" % (len(quotes)))
                    self.awse.upload_quotes_to_s3(quotes, collection_name=ticker['SravzId'])
            except Exception:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)