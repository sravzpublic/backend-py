import datetime, urllib.request, json
from src.util import settings, logger
from src.services import aws
from src.services import mdb

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    def get_eodhistoricaldata_historical_etf_quotes(self, tickers = [], upload_to_db = False, ndays_back=None):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.ETF_ASSETS_COLLECTION)
        for ticker in tickers:
            try:
                # Only US quotes are avaiable
                if ticker.get('Country') == "USA" and not self.awse.is_quote_updated_today(ticker['SravzId'], settings.constants.S3_TARGET_CONTABO):
                    url = "{0}/api/eod/{1}.US?api_token={2}&order=d&fmt=json".format(settings.constants.EOD_URL, ticker['ETFCode'], settings.constants.EODHISTORICALDATA_API_KEY)
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
                        # self.awse.upload_quotes_to_s3(quotes, collection_name=ticker['SravzId'])
                        self.awse.upload_quotes_to_contabo(quotes, collection_name=ticker['SravzId'], target=settings.constants.S3_TARGET_CONTABO)
                        self.awse.upload_quotes_to_contabo(quotes, collection_name=ticker['SravzId'], target=settings.constants.S3_TARGET_IDRIVEE2)
            except Exception:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)

if __name__ == "__main__":
    e = engine()
    # e.get_eodhistoricaldata_historical_etf_quotes(tickers = [{
    # "_id" : "",
    # "ETFCode" : "AADR",
    # "Country" : "USA",
    # "ETFName" : "AdvisorShares Dorsey Wright ADR ETF",
    # "Exchange" : "US",
    # "ISIN" : "US00768Y2063",
    # "SravzId" : "etf_us_aadr"
    # }], upload_to_db=True)
    e.get_eodhistoricaldata_historical_etf_quotes(tickers = [], upload_to_db=True)