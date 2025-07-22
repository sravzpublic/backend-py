import datetime, urllib.request, json
from src.util import settings, logger
from src.services import aws
from src.services import mdb

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    def upload_quotes_to_db(self, data, collection_name, db_type='live', ndays_back=None):
        if db_type == 'live':
            mdbe = mdb.engine()
            quotes_stocks_col = mdbe.get_collection(collection_name)
            for item in data:
                item['Time'] = datetime.datetime.now(datetime.UTC)
                quotes_stocks_col.update_one({"SravzId": item['SravzId']}, {
                    "$set": item}, upsert=True)
        elif db_type == 'historical':
            self.awse.upload_quotes_to_s3(data, collection_name)

    def get_eodhistoricaldata_realtime_quotes(self, tickers = [], upload_to_db = False):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.ETF_ASSETS_COLLECTION)
        quotes = []
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/real-time/{0}?api_token={1}&fmt=json".format(ticker['ETFCode'], settings.constants.EODHISTORICALDATA_API_KEY)
                self.logger.info("processing %s" % (url))
                json_data = urllib.request.urlopen(url).read()
                quote  = json.loads(json_data)
                ticker.pop('_id')
                ticker ["Time"] = datetime.datetime.fromtimestamp(int(quote.pop("timestamp")))
                ticker ["Ticker"] = quote.pop("code")
                ticker ["Volume"] = quote.pop("volume")
                ticker ["Open"] = quote.pop("open")
                ticker ["High"] = quote.pop("high")
                ticker ["Low"] = quote.pop("low")
                ticker ["Last"] = ticker ["Close"] = quote.pop("close")
                ticker ["PreviousClose"] = quote.pop("previousClose")
                ticker ["Change"] = quote.pop("change")
                ticker ["PercentChange"] = quote.pop("change_p")
                quotes.append(ticker)
            except Exception:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
        if upload_to_db:
            self.upload_quotes_to_db(quotes, collection_name='quotes_etf', db_type='live')


if __name__ == "__main__":
    e = engine()
    e.get_eodhistoricaldata_realtime_quotes(tickers = [], upload_to_db=True)