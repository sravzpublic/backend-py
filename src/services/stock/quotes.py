from src.util import settings, logger
from src.services import mdb
import datetime
import json
import urllib.request
from src.services.assets import indices

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    def get_quotes_from_eodhistoricaldata(self, tickers=[]):
        '''
            e = engine()
            e.get_quotes_from_eodhistoricaldata(tickers = ['A', 'AAL', 'AAP'])
        '''
        quotes = []
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/real-time/{0}.US?api_token={1}&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
                self.logger.info("processing %s" % (url))
                json_data = urllib.request.urlopen(url).read()
                quote  = json.loads(json_data)
                quote ["Ticker"] = ticker['Code']
                quote ["Time"] = datetime.datetime.fromtimestamp(int(quote.pop("timestamp")))
                quote ["Code"] = quote.pop("code")
                quote ["Volume"] = quote.pop("volume")
                quote ["Open"] = quote.pop("open")
                quote ["High"] = quote.pop("high")
                quote ["Low"] = quote.pop("low")
                quote ["Last"] = quote ["Close"] = quote.pop("close")
                quote ["PreviousClose"] = quote.pop("previousClose")
                quote ["Change"] = quote.pop("change")
                quote ["PercentChange"] = quote.pop("change_p")
                ticker.update(quote)
                quotes.append(ticker)
            except Exception as e:
                self.logger.error(f'Failed to process quote for ticker {ticker}', exc_info=True)
        return quotes

    def get_quotes(self, upload_to_db=False, tickers=[]):
        '''
            e = engine()
            e.get_snp_quotes(tickers = ['AAPL','GOOG','IBM','C','SPX','UHG','FB'])
        '''
        tickers = {}
        for index in settings.constants.INDEX_COMPONENTS_QUOTES_TO_UPLOAD:
            [tickers.update({x['Code']: x}) for x in json.loads(indices.get_index_components_from_s3(index))['Components'].values()]
        # tickers = (list(set(tickers)))
        quotes = self.get_quotes_from_eodhistoricaldata(list(tickers.values()))
        self.upload_quotes_to_db(quotes)

    def upload_quotes_to_db(self, data, collection_name='quotes_stocks'):
        mdbe = mdb.engine()
        quotes_stocks_col = mdbe.get_collection(collection_name)
        for item in data:
            item['Time'] = datetime.datetime.now(datetime.UTC)
            item['SNP'] = True
            item['Country'] = 'US'
            item['SravzId'] = "stk_us_%s" % (item['Ticker']).lower()
            quotes_stocks_col.update_one({"Ticker": item['Ticker']}, { "$set": item}, upsert=True)
