from src.util import settings, logger, helper
from fredapi import Fred
from src.services import mdb
import datetime
import requests, urllib.request, json
from src.services import webcrawler, aws
from bs4 import BeautifulSoup
# from dask.distributed import Client


def process_ticker(ticker):
    sravz_id, code = ticker
    awse = aws.engine()
    url = "https://eodhistoricaldata.com/api/eod/{0}.CC?api_token={1}&order=d&fmt=json".format(code, settings.constants.EODHISTORICALDATA_API_KEY2)
    _logger = logger.RotatingLogger(__name__).getLogger()
    _logger.info("processing %s" % (url))
    json_data = urllib.request.urlopen(url).read()
    data  = json.loads(json_data)
    quotes = []
    for quote in data:
        quote['SravzId'] = sravz_id
        quote['Date'] = datetime.datetime.strptime(quote.pop('date'), '%Y-%m-%d')
        quote["Volume"] = quote.pop("volume")
        quote["Open"] = quote.pop("open")
        quote["High"] = quote.pop("high")
        quote["Low"] = quote.pop("low")
        quote["Close"] = quote.pop("close")
        quote["AdjustedClose"] = quote.pop("adjusted_close")
        quotes.append(quote)
    _logger.info("Uploading %s quotes to db" % (len(quotes)))
    awse.upload_quotes_to_s3(quotes, sravz_id)
    return f"Ticker {sravz_id} processed"

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()
        self.awse = aws.engine()

    def get_crypto_quotes(self, upload_to_db=False):
        # url = 'https://finance.yahoo.com/currencies/'
        # self.logger.info("processing %s" % (url))
        # quotes = self.we.get_data_from_html_table(
        #     None, None, url=url, table_attrs={"data-reactid": "15"})
        # quotes_data = []
        # for item in quotes:
        #     name = item.get('Name').split("/")
        #     if name[0] in ['ETH', 'BTC']:
        #         item['SravzId'] = "crypto_{0}_{1}".format(name[0], name[1]).lower()
        #     else:
        #         continue
        #     item['Ticker'] = item.pop('Symbol')
        #     item['Change'] = helper.util.getfloat(
        #         self.we.sanitize(item.pop('Change')))
        #     item['Last'] = helper.util.getfloat(
        #         self.we.sanitize(item.pop('LastPrice')))
        #     item['PercentChange'] = item.pop('%Change')
        #     item.pop('52WeekRange')
        #     item.pop('DayChart')
        #     quotes_data.append(item)

        url = 'https://coinmarketcap.com/coins/'
        data = self.we.get_data_from_html_table(
            None, None, url=url,  table_attrs={"id": "currencies"})
        quotes = []
        for item in data:
            try:
                quote = {}
                quote['Name'] = item.get('Name').split('\n\n')[1].lower()
                quote['Ticker'] = item.get('Name').split('\n\n')[0].lower()
                if quote['Ticker'] not in settings.constants.CRYPTO_TICKERS:
                    continue
                quote['SravzId'] = "crypto_{0}_{1}".format(
                    quote['Ticker'], 'usd').lower()
                quote['MarketCap'] = item.get('MarketCap')
                quote['Last'] = helper.util.getfloat(
                    self.we.sanitize(item.get('Price')))
                quote['Volume'] = helper.util.getfloat(
                    self.we.sanitize(item.get('Volume(24h)')))
                quote['CirculatingSupply'] = helper.util.getfloat(
                    self.we.sanitize(item.get('CirculatingSupply')))
                quote['PercentChange'] = item.get('Change(24h)')
                quotes.append(quote)
            except Exception:
                pass
        if upload_to_db:
            self.upload_quotes_to_db(
                quotes, collection_name='quotes_crypto', db_type='live')

    def get_historical_crypto_quotes(self, tickers=[], upload_to_db=False, from_date=None, ndays_back=None):
        '''
            Uploads rates data to mongodb
        '''
        tickers = tickers or settings.constants.CRYPTO_QUOTES_URL.keys()
        for ticker in tickers:
            quotes = []
            url = settings.constants.CRYPTO_QUOTES_URL[ticker]
            self.logger.info("processing %s" % (url))
            html_data = requests.get(url).text
            soup = BeautifulSoup(html_data, 'html.parser')
            parent = soup.find("div", attrs={"id": "historical-data"})
            table = parent.find('table', attrs={"class": "table"})
            quotes = self.we.get_data_from_html_table_ignore_missing_tags(
                table)
            #Reverse data from earliest to latest date
            quotes[::-1]
            for quote in quotes:
                quote['Date'] = datetime.datetime.strptime(
                    quote['Date'], '%b %d, %Y')
                for col in ['High', 'Low', 'Volume', 'MarketCap']:
                    quote[col] = helper.util.getfloat(
                        self.we.sanitize(quote.pop(col)))
                quote['Open'] = helper.util.getfloat(
                    self.we.sanitize(quote.pop('Open*')))
                quote['Close'] = helper.util.getfloat(
                    self.we.sanitize(quote.pop('Close**')))
                quote['Last'] = quote.pop('Close')
            if upload_to_db:
                self.upload_quotes_to_db(
                    quotes, collection_name=ticker, db_type='historical', ndays_back=ndays_back)

        # Upload rest of the inteest rates: https://www.global-rates.com/interest-rates/central-banks/central-banks.aspx

    def process_ticker(self, ticker, quotes, upload_to_db=False):
        try:
            if upload_to_db:
                self.upload_quotes_to_db(
                    quotes, collection_name=ticker, db_type='historical')
        except Exception:
            self.logger.error(
                'Failed to upload quote {0}'.format(ticker), exc_info=True)

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
            # mdbe_historical = mdb.engine(
            #     database_name='historical', database_url='historical_url')
            # quotes_col = mdbe_historical.get_collection(collection_name)
            # for item in data:
            #     if ndays_back and (datetime.datetime.now() - item['Date']).days > ndays_back:
            #         continue
            #     quotes_col.update_one({"Date": item['Date']}, {
            #         "$set": item}, upsert=True)

# BTC, ETH, USDT, BNB, ADA, DOGE, XRP, USDC, DOT, UNI
    def get_eodhistoricaldata_crypto_quotes(self, tickers = [], upload_to_db = False):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.CRYPTO_ASSETS_COLLECTION)
        quotes = []
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/real-time/{0}.CC?api_token={1}&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
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
            self.upload_quotes_to_db(quotes, collection_name='quotes_crypto', db_type='live')


    def get_eodhistoricaldata_historical_crypto_quotes(self, tickers = [], upload_to_db = False, ndays_back=None):
        mdbe = mdb.engine()
        _logger = logger.RotatingLogger(__name__).getLogger()
        # client = Client(f'{settings.constants.DASK_SCHEDULER_HOST_NAME}:8786')
        _logger.info(f"Connected to Dask Scheduler at {settings.constants.DASK_SCHEDULER_HOST_NAME}")
        tickers = tickers or mdbe.get_collection_items(settings.constants.CRYPTO_ASSETS_COLLECTION)
        self.logger.info(f"Processing crypto tickers - {len(tickers)}")
        result = [process_ticker(ticker) for ticker in [(ticker['SravzId'], ticker["Code"]) for ticker in tickers]]
        #future = client.map(process_ticker, [(ticker['SravzId'], ticker["Code"]) for ticker in tickers])
        #result = client.gather(future)
        self.logger.info(f"Processed {len(tickers)} crypto tickers: {result}")
