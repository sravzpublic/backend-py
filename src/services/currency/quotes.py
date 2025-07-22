from src.util import settings, logger, helper
from fredapi import Fred
from src.services import mdb, aws
import datetime, json, urllib
from src.services import webcrawler
from bs4 import BeautifulSoup


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        # self.we = webcrawler.engine()
        self.awse = aws.engine()

    # def get_currency_quotes(self, upload_to_db=False, db_type=settings.constants.DB_TYPE_LIVE):

    #     quotes_process = []
    #     url = 'https://finance.yahoo.com/currencies/'
    #     self.logger.info("processing %s" % (url))
    #     _yahoo_quotes = self.we.get_data_from_html_table(
    #         None, None, url=url, table_attrs={"data-reactid": "15"})
    #     yahoo_quotes = []
    #     for item in yahoo_quotes:
    #         name = item.get('Name').split("/")
    #         if name[0] in ['ETH', 'BTC']:
    #             continue
    #         else:
    #             item['SravzId'] = "forex_{0}_{1}".format(name[0], name[1]).lower()
    #         quotes_process.append(item['SravzId'])
    #         item['Ticker'] = item.pop('Symbol')
    #         item['Change'] = helper.util.getfloat(
    #             self.we.sanitize(item.pop('Change')))
    #         item['Last'] = helper.util.getfloat(
    #             self.we.sanitize(item.pop('LastPrice')))
    #         item['PercentChange'] = item.pop('%Change')
    #         item.pop('52WeekRange')
    #         item.pop('DayChart')
    #         yahoo_quotes.append(item)

    #     url = 'https://www.moneycontrol.com/mccode/currencies/'
    #     self.logger.info("processing %s" % (url))
    #     data = self.we.get_data_from_url(url)
    #     soup = BeautifulSoup(data, 'html.parser')
    #     parent = soup.find("div", attrs={"class": "currency_table"})
    #     tables = parent.find_all('table')
    #     mc_quotes = self.we.get_data_from_html_table_ignore_missing_tags(
    #         tables[0], th_is_present_thead_absent=True)
    #     mc_quotes = mc_quotes[2:]
    #     mc_quotes_to_use = []
    #     for item in mc_quotes:
    #         # Check if direct quote
    #         if item.get('CURRENCYPAIR') and "/" in item.get('CURRENCYPAIR'):
    #             name = item.get('CURRENCYPAIR').split("/")
    #             item['Name'] = item.pop('CURRENCYPAIR')
    #             item['SravzId'] = "forex_{0}_{1}".format(
    #                 name[0], name[1]).lower()
    #             if item['SravzId'] in quotes_process:
    #                 self.logger.info(
    #                     "Quote %s already processed. Ignoring." % (item['SravzId']))
    #                 continue
    #             quotes_process.append(item['SravzId'])
    #             item['Ticker'] = "{0}=X".format(''.join(name))
    #             item['Last'] = helper.util.getfloat(
    #                 self.we.sanitize(item.pop('CURRENTSPOT')))
    #             item['Open'] = helper.util.getfloat(
    #                 self.we.sanitize(item.pop('OPEN')))
    #             item['High'] = helper.util.getfloat(
    #                 self.we.sanitize(item.pop('HIGH')))
    #             item['Low'] = helper.util.getfloat(
    #                 self.we.sanitize(item.pop('LOW')))
    #             item['Close'] = helper.util.getfloat(
    #                 self.we.sanitize(item.pop('CLOSE')))
    #             item.pop('TIME')
    #             mc_quotes_to_use.append(item)

    #     quotes_data = yahoo_quotes + mc_quotes_to_use
    #     if upload_to_db and db_type == settings.constants.DB_TYPE_LIVE:
    #         self.upload_quotes_to_db(quotes_data, collection_name='quotes_currency',
    #                                  db_type=db_type)
    #     elif upload_to_db and db_type == settings.constants.DB_TYPE_HISTORICAL:
    #         for item in quotes_data:
    #             if item['SravzId'] in settings.constants.ST_LOUIS_FRED_CURRENCY_MAP.values():
    #                 self.upload_quotes_to_db([{
    #                     'Date': datetime.datetime.now().strftime("%Y-%m-%d"),
    #                     'Settle': item['Last']
    #                 }], item['SravzId'], db_type=db_type)
    #             else:
    #                 self.logger.info(
    #                     "Historical collection for quote {0} not found".format(item['SravzId']))

    # def get_historical_currency_quotes(self, tickers=[], upload_to_db=False, from_date=None, ndays_back=None):
    #     '''
    #         Uploads currency data to mongodb uses ST_LOUIS_FRED
    #     '''
    #     tickers = tickers or settings.constants.ST_LOUIS_FRED_CURRENCY_MAP.keys()
    #     for ticker in tickers:
    #         try:
    #             self.logger.info("Processing quote: {0}".format(ticker))
    #             fred = Fred(api_key=settings.constants.ST_LOUIS_FRED_API_KEY)
    #             data = fred.get_series(ticker)
    #             if from_date:
    #                 data = data.loc[from_date:]
    #             if ndays_back:
    #                 data = data.loc[helper.util.get_n_days_back_date(
    #                     ndays_back):]
    #             quotes = []
    #             for key in data.keys():
    #                 quote = {}
    #                 quote['Date'] = key
    #                 quote['Last'] = helper.util.getfloat(data[key])
    #                 quotes.append(quote)
    #             if upload_to_db:
    #                 self.upload_quotes_to_db(
    #                     quotes, collection_name=settings.constants.ST_LOUIS_FRED_CURRENCY_MAP[
    #                         ticker],
    #                     db_type='historical', ndays_back=ndays_back)
    #         except Exception:
    #             self.logger.error(
    #                 'Failed to process quote {0}'.format(ticker), exc_info=True)

    def get_eodhistoricaldata_live_currency_quotes(self, tickers = [], upload_to_db = False):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.FOREX_ASSETS_COLLECTION)
        quotes = []
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/real-time/{0}.FOREX?api_token={1}&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
                self.logger.info("processing %s" % (url))
                json_data = urllib.request.urlopen(url).read()
                quote  = json.loads(json_data)
                ticker.pop('_id')
                timestamp = quote.pop("timestamp")
                if isinstance(timestamp, int):
                    ticker ["Time"] = datetime.datetime.fromtimestamp(int(timestamp))
                else:
                    ticker ["Time"] = timestamp
                ticker ["Ticker"] = quote.pop("code")
                ticker ["Volume"] = quote.pop("volume")
                ticker ["Open"] = quote.pop("open")
                ticker ["High"] = quote.pop("high")
                ticker ["Low"] = quote.pop("low")
                ticker ["Last"] = quote ["Close"] = quote.pop("close")
                ticker ["PreviousClose"] = quote.pop("previousClose")
                ticker ["Change"] = quote.pop("change")
                ticker ["PercentChange"] = quote.pop("change_p")
                quotes.append(ticker)
            except Exception as e:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
        if upload_to_db:
            self.upload_quotes_to_db(quotes, collection_name='quotes_currency', db_type=settings.constants.DB_TYPE_LIVE)

    # def get_eodhistoricaldata_live_currency_quotes(self, tickers = [], upload_to_db = False, ndays_back=None):
    #     '''
    #         https://eodhistoricaldata.com/api/real-time/AEDAUD.FOREX?api_token={1}&order=d&fmt=json
    #     '''
    #     mdbe = mdb.engine()
    #     tickers = tickers or mdbe.get_collection_items(settings.constants.FOREX_ASSETS_COLLECTION)
    #     for ticker in tickers:
    #         try:
    #             url = "https://eodhistoricaldata.com/api/real-time/{0}.FOREX?api_token={1}&order=d&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY)
    #             self.logger.info("processing %s" % (url))
    #             json_data = urllib.request.urlopen(url).read()
    #             data  = json.loads(json_data)
    #             ticker.pop('_id')
    #             quotes = []
    #             for quote in data:
    #                 quote['Date'] = datetime.datetime.strptime(quote.pop('date'), '%Y-%m-%d')
    #                 quote["Volume"] = quote.pop("volume")
    #                 quote["Open"] = quote.pop("open")
    #                 quote["High"] = quote.pop("high")
    #                 quote["Low"] = quote.pop("low")
    #                 quote["Close"] = quote.pop("close")
    #                 quote["AdjustedClose"] = quote.pop("adjusted_close")
    #                 quotes.append(quote)
    #             if upload_to_db:
    #                 #self.logger.info("Uploading %s quotes to db" % (len(quotes)))
    #                 self.upload_quotes_to_db(quotes, collection_name='quotes_currency', db_type=settings.constants.DB_TYPE_LIVE)
    #                 #self.awse.upload_quotes_to_s3(quotes, ticker['SravzId'])
    #         except Exception:
    #             self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)

    def get_eodhistoricaldata_historical_currency_quotes(self, tickers = [], upload_to_db = False, ndays_back=None):
        '''
            https://eodhistoricaldata.com/api/eod/AEDAUD.FOREX?api_token={1}&order=d&fmt=json
        '''
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.FOREX_ASSETS_COLLECTION)
        for ticker in [ticker for ticker in tickers if not self.awse.is_quote_updated_today(ticker['SravzId'])]:
            try:
                url = "https://eodhistoricaldata.com/api/eod/{0}.FOREX?api_token={1}&order=d&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
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
                    #self.logger.info("Uploading %s quotes to db" % (len(quotes)))
                    #self.upload_quotes_to_db(quotes, collection_name=ticker['SravzId'], db_type='historical', ndays_back = ndays_back)
                    self.awse.upload_quotes_to_s3(quotes, ticker['SravzId'])
            except Exception:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)

    def upload_quotes_to_db(self, data, collection_name, db_type='live', ndays_back = None):
        if db_type == 'live':
            mdbe = mdb.engine()
            quotes_stocks_col = mdbe.get_collection(collection_name)
            for item in data:
                try:
                    item['Time'] = datetime.datetime.now(datetime.UTC)
                    quotes_stocks_col.update_one({"SravzId": item['SravzId']}, {
                        "$set": item}, upsert=True)
                except Exception:
                    self.logger.error('Failed to process quote {0}'.format(item), exc_info=True)
        elif db_type == 'historical':
            mdbe_historical = mdb.engine(
                database_name='historical', database_url='historical_url')
            quotes_col = mdbe_historical.get_collection(collection_name)
            for item in data:
                try:
                    if ndays_back and (datetime.datetime.now() - item['Date']).days > ndays_back:
                        continue
                    quotes_col.update_one({"Date": item['Date']}, {
                        "$set": item}, upsert=True)
                except Exception:
                    self.logger.error('Failed to process quote {0}'.format(item), exc_info=True)
