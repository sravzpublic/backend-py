from src.util import settings, logger
from src.services import mdb, aws
import datetime, json, urllib


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    #### Bond historical data not supported
    # def get_eodhistoricaldata_live_bond_quotes(self, tickers = [], upload_to_db = False):
    #     mdbe = mdb.engine()
    #     tickers = tickers or mdbe.get_collection_items(settings.constants.BOND_ASSETS_COLLECTION)
    #     quotes = []
    #     for ticker in tickers:
    #         try:
    #             url = "https://eodhistoricaldata.com/api/real-time/{0}.FOREX?api_token={1}&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY)
    #             self.logger.info("processing %s" % (url))
    #             json_data = urllib.request.urlopen(url).read()
    #             quote  = json.loads(json_data)
    #             ticker.pop('_id')
    #             timestamp = quote.pop("timestamp")
    #             if isinstance(timestamp, int):
    #                 ticker ["Time"] = datetime.datetime.fromtimestamp(int(timestamp))
    #             else:
    #                 ticker ["Time"] = timestamp
    #             ticker ["Ticker"] = quote.pop("code")
    #             ticker ["Volume"] = quote.pop("volume")
    #             ticker ["Open"] = quote.pop("open")
    #             ticker ["High"] = quote.pop("high")
    #             ticker ["Low"] = quote.pop("low")
    #             ticker ["Last"] = quote ["Close"] = quote.pop("close")
    #             ticker ["PreviousClose"] = quote.pop("previousClose")
    #             ticker ["Change"] = quote.pop("change")
    #             ticker ["PercentChange"] = quote.pop("change_p")
    #             quotes.append(ticker)
    #         except Exception as e:
    #             self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
    #     if upload_to_db:
    #         self.upload_quotes_to_db(quotes, collection_name='quotes_currency', db_type=settings.constants.DB_TYPE_LIVE)


    def get_eodhistoricaldata_historical_bond_quotes(self, tickers = [], upload_to_db = True, ndays_back=None):
        '''
            https://eodhistoricaldata.com/api/eod/US910047AG49.BOND?api_token=YOUR_API_TOKEN&order=d&fmt=json&from=2017-08-01
        '''
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.BOND_ASSETS_COLLECTION)
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/eod/{0}.BOND?api_token={1}&order=d&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
                self.logger.info("processing %s" % (url))
                json_data = urllib.request.urlopen(url).read()
                data  = json.loads(json_data)
                ticker.pop('_id')
                quotes = []
                for quote in data:
                    quote['Date'] = datetime.datetime.strptime(quote.pop('date'), '%Y-%m-%d')
                    quote["Last"] = quote.pop("price")
                    quote["Yield"] = quote.pop("yield")
                    quote["Volume"] = quote.pop("volume")
                    quotes.append(quote)
                if upload_to_db:
                    self.logger.info("Uploading %s quotes to s3" % (len(quotes)))
                    self.awse.upload_quotes_to_s3(quotes, ticker['SravzId'])
            except Exception:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
