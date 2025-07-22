import datetime, urllib.request, json
from src.util import settings, logger
from src.services import aws
from src.services import mdb
from src.services.quotes_providers import yahoo
import requests

LOGGER = logger.RotatingLogger(__name__).getLogger()

def upload_ticker(ticker, upload_to_db = True, check_if_uploaded_today = False):
    '''
    @parm check_if_uploaded_today - ticker ignored if uploaded today
    from src.services.etfs.mutual_funds_historical_quotes import upload_ticker
    upload_ticker({'_id': None, 'APICode':'AAAEX.US', 'SravzId': 'AAAEX.US'})
    Not used anymore. Uses DarQube
    '''
    awse = aws.engine()      
    if check_if_uploaded_today and awse.is_quote_updated_today(ticker['SravzId'], settings.constants.S3_TARGET_CONTABO):
        LOGGER.info("Ticker %s uploaded today. Ignored..." % (ticker))
        return (ticker, True)
    try:
        url = "https://eodhistoricaldata.com/api/eod/{0}?api_token={1}&order=d&fmt=json".format(ticker['APICode'], settings.constants.EODHISTORICALDATA_API_KEY)
        LOGGER.info("processing %s" % (url))
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
        if upload_to_db:
            LOGGER.info("Uploading %s quotes to s3" % (len(quotes)))
            awse.upload_quotes_to_contabo(quotes, collection_name=ticker['SravzId'], target=settings.constants.S3_TARGET_CONTABO)
            awse.upload_quotes_to_contabo(quotes, collection_name=ticker['SravzId'], target=settings.constants.S3_TARGET_IDRIVEE2)
            return (ticker, True)
    except Exception:
        LOGGER.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
    return (ticker, False)

def upload_ticker_darqube(ticker, upload_to_db = True):
    '''
    from src.services.etfs.mutual_funds_historical_quotes import upload_ticker_darqube
    upload_ticker_darqube({'APICode': 'JBALX.US', 'SravzId': 'fund_us_jbalx'})
    Not used anymore. Uses DarQube
    '''
    awse = aws.engine()
    try:
        url = "https://api.darqube.com/data-api/market_data/historical/{0}?token={1}&start_date=0&interval=1d".format(ticker['APICode'], settings.constants.DARQUBE_API_TOKEN)
        LOGGER.info("processing %s" % (url))
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        data=response.json()
        quotes = []
        for quote in data:
            quote['Date'] = datetime.datetime.fromtimestamp(quote.pop('time')).strftime('%Y-%m-%d') #datetime.datetime.strptime(quote.pop('time'), '%Y-%m-%d')
            quote["Volume"] = quote.pop("volume")
            quote["Open"] = quote.pop("open")
            quote["High"] = quote.pop("high")
            quote["Low"] = quote.pop("low")
            quote["Close"] = quote.pop("close")
            quote["AdjustedClose"] = quote.pop("adjusted_close")
            quotes.append(quote)
        if upload_to_db:
            LOGGER.info("Uploading %s quotes to s3" % (len(quotes)))
            awse.upload_quotes_to_s3(quotes, collection_name=ticker['SravzId'])
            return (ticker, True)
    except Exception:
        LOGGER.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
    return (ticker, False)


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    def get_eodhistoricaldata_historical_mutual_fund_quotes(self, tickers = [], upload_to_db = False, ndays_back=None):
        us_mf_tickers = self.get_all_mf_tickers(tickers)
        if us_mf_tickers:
            # client = Client(f'{settings.constants.DASK_SCHEDULER_HOST_NAME}:8786')
            # future = client.map(upload_ticker_darqube, us_mf_tickers)
            # future = client.map(upload_ticker, us_mf_tickers)
            # result = client.gather(future)
            # future = client.map(upload_ticker, us_mf_tickers)
            awse = aws.engine()             
            [upload_ticker(ticker) for ticker in us_mf_tickers if not awse.is_quote_updated_today(ticker['SravzId'], 
                                                                                                  settings.constants.S3_TARGET_CONTABO)]
            # print(result)

    def get_all_mf_tickers(self, tickers, cache = False):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.EXCHANGE_SYMBOLS_COLLECTION, cache=cache)
        us_mf_tickers = []
        for ticker in tickers:
            # Only US quotes are avaiable
            if ticker.get('Country') == "USA" and ticker.get('Exchange') == "NMFQS":
                us_mf_tickers.append(
                    {
                        'APICode': ticker['APICode'],
                        'SravzId': ticker['SravzId']
                    }
                )
        return us_mf_tickers

    def get_all_mf_tickers_not_uploaded_today(self, tickers):
        awse = aws.engine() 
        return [ticker for ticker in tickers if not awse.is_quote_updated_today(ticker['SravzId'], 
                                                                                                  settings.constants.S3_TARGET_CONTABO)]


if __name__ == '__main__':
    e = engine()
    e.get_eodhistoricaldata_historical_mutual_fund_quotes()








