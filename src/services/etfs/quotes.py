import pycountry
from src.util import settings, logger, helper
from src.services import mdb
import re, datetime, pymongo, sys, traceback, json, urllib.request
from src.services.quotes_providers import marketwatch, moneycontrol, yahoo

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.mdbe = mdb.engine()


    def upload_index_quotes_to_db(self, data, collection_name = 'quotes_index'):
        quotes_index_col = self.mdbe.get_collection(collection_name)
        world_capitals = self.mdbe.get_collection_as_df(settings.constants.WORLD_CAPITALS_COLLECTION)
        world_major_indices = self.mdbe.get_collection_as_df(settings.constants.WORLD_MAJOR_INDICES_COLLECTION)
        world_capitals = world_capitals.set_index('CountryName')
        world_capitals.index = world_capitals.index.str.lower()
        for item in data:
            try:
                item['Time'] = datetime.datetime.now(datetime.UTC)
                if not item.get('SravzId'):
                    item['SravzId'] = "idx_us_%s"%(item['Ticker'].lower())
                if not item.get('Country'):
                    item['Country'] = 'Unknown'
                world_capital = None
                try:
                    country = pycountry.countries.lookup(item['Country'].lower())
                    if country.alpha_2.lower() in world_capitals.index:
                        world_capital = world_capitals.loc[[country.alpha_2.lower()]].to_dict(orient='records').pop()
                    elif country.alpha_3.lower() in world_capitals.index:
                        world_capital = world_capitals.loc[[country.alpha_3.lower()]].to_dict(orient='records').pop()
                    elif country.name.lower() in world_capitals.index:
                        world_capital = world_capitals.loc[[country.name.lower()]].to_dict(orient='records').pop()
                except LookupError:
                    if item['Country'].lower() in world_capitals.index:
                        world_capital = world_capitals.loc[[item['Country'].lower()]].to_dict(orient='records').pop()
                    self.logger.warn('Pycountry not found for {0}. Setting world_capital to {1}'.format(item['Country'].lower(), world_capital))
                if world_capital:
                    world_capital['CapitalLatitude'] = helper.util.getfloat(world_capital['CapitalLatitude'])
                    world_capital['CapitalLongitude'] = helper.util.getfloat(world_capital['CapitalLongitude'])
                    item.update(world_capital)
                if any([x in item['Ticker'].lower() for x in world_major_indices['IndexName'].values]):
                    item['MajorIndex'] = True
                else:
                    item['MajorIndex'] = False
                #if country: #world_capitals.index[1]): # item['Country'] in world_capitals.index:
                quotes_index_col.update_one({"Ticker" : item['Ticker'] }, {"$set": item}, upsert=True)
            except:
                self.logger.exception('Error uploading: %s to quotes_index' % (str(item)))


    def get_eodhistoricaldata_index_quotes(self, tickers = [], upload_to_db = False):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.INDEX_ASSETS_COLLECTION)
        quotes = []
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/real-time/{0}.INDX?api_token={1}&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
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
            self.upload_index_quotes_to_db(quotes)
