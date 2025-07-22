import  requests, datetime, json, pymongo
import pandas as pd
from src.util import settings, helper, logger
from src.services import webcrawler
from src.services import mdb, aws
from src.services import idgenerator
from src.services.price_helpers.historical_currency import engine_currency
from src.services.price_helpers import util
from titlecase import titlecase
from src.services.price_helpers.util import Util
import urllib.request


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    """description of class"""
    def get_historical_price(self, asset_name, asset_type = None):
        pec = engine_currency()
        if asset_type == settings.constants.CURRENCY:
            return pec.get_historical_price(asset_name)
        else:
            setting = [x for x in settings.constants.all_commodities if x['name'] == asset_name][0]
            if settings.constants.read_from_file:
                with open(settings.constants.fake_data_directory + asset_name + '_20161228.json', 'r') as f:
                    data = json.loads(f.read())
            else:
                r = requests.get(setting['price_url'])
                data = r.json()
            price_data = setting['price_lambda'](data)
            price_columns = setting['price_column_lambda'](data)
            df = pd.DataFrame(price_data, columns=price_columns)
            df[price_columns[0]] = pd.to_datetime(df[price_columns[0]])
            df = df.set_index([price_columns[0]])
            df.sort_index(inplace = True)
            df.dropna(inplace = True)
            return df

    def get_current_price(self, upload_to_db = False):
        we = webcrawler.engine()
        commodities_url = settings.constants.quotes['commodities']['url']
        data = we.get_data_from_url(commodities_url)
        c_quotes_data = we.get_data_from_html_table(data, "genTbl closedTbl crossRatesTbl",
                                                    header_lambda = lambda x: x.replace('.','').replace('%', '_Pct'),
                                                    header_extractor = { 0: lambda row: "Country"},
                                                    column_extractor = { 0: lambda row: row.find_all('span')[0].attrs['class'][1]})
        if upload_to_db and c_quotes_data:
            self.upload_price_to_db(c_quotes_data, 'quotes_commodities')
        return c_quotes_data

    def get_current_price_cnbc(self, upload_to_db = False):
        we = webcrawler.engine()
        quotes = []
        for url in settings.constants.quotes['cnbc_commodities_urls']:
            try:
                self.logger.info("Fetching quote for url: %s"%(url))
                data = we.get_data_from_url(url)
                data =data.replace("webQuoteRequest(", "")[:-1]
                data = json.loads(data)
                item = data['QuickQuoteResult']['QuickQuote']
                name = item['name'].replace(" ", "").replace("(", "_").replace(")", "").replace("'", "_").lower()
                Sravz_Id = "fut_%s_%s_%s"%(name, (item['currencyCode']),(item['altSymbol']))
                price_info = {
                    "SravzId" : Sravz_Id.lower(),
                    "Last" : item["last"],
                    "Commodity" : item["shortName"].lower(),
                    "Name" : item["name"].lower(),
                    "Chg" : item["change"],
                    "Country" : item["countryCode"],
                    "Month" : item["name"].split("(")[1].replace("'", " ").split(")")[0],
                    'Open': item["open"],
                    "High" : item["high"],
                    "Low" : item["low"],
                    "Time" : item["last_time"],
                    "Chg_Pct" : item["change_pct"],
                    "Exchange": item["exchange"],
                    'Symbol': item["altSymbol"],
                    'CNBCSymbol': item["symbol"],
                    'Volume': item["volume"],
                    'Open Interest': item["open_interest"],
                    'Settle': item["settlePrice"],
                    'SettleDate': item["settleDate"],
                    }
                quotes.append(price_info)
            except Exception as e:
                self.logger.error('Failed to get CNBC quote from url %s'%(url), exc_info=True)
        if upload_to_db and quotes:
            self.upload_price_to_db(quotes, 'quotes_commodities')
            return None
        return quotes

    def upload_end_of_day_cnbc_price_to_mdb(self):
        mdbe = mdb.engine(database_name='historical', database_url='historical_url')
        quotes = self.get_current_price_cnbc()
        self.populate_unique_id(quotes)
        for quote in quotes:
            print("Processing quote for Sravz ID %s"%(quote["SravzId"]))
            collection_name = Util.get_hostorical_collection_name_from_sravz_id(quote["SravzId"])
            c_quotes_col = mdbe.get_collection(collection_name)
            quote["Date"] = quote["SettleDate"]
            historical_data = self.get_historical_datapoint(quote)
            c_quotes_col.update_one({"Date": historical_data['Date']}, {"$set": historical_data}, upsert=True)

    def populate_unique_id(self, data):
        idgeneratore = idgenerator.engine()
        for item in data:
            item["SravzId"] = idgeneratore.get_unique_id("Future", item).lower()

    def upload_price_to_db(self, data, collection_name):
        mdbe = mdb.engine()
        self.populate_unique_id(data)
        c_quotes_col = mdbe.get_collection(collection_name)
        for item in data:
            if not any([to_exclude in item['SravzId'] for to_exclude in settings.constants.commodities_to_exclude]):
                item['pricecapturetime'] = datetime.datetime.now(datetime.UTC)
                item['SravzId'] = helper.get_generic_sravz_id(item['SravzId'])
                c_quotes_col.update({"SravzId": item['SravzId']}, {"$set": item}, upsert=True)

    def upload_all_quandl_to_db(self, sravzids = None, ndays_back = None):
        """
            #Use this function to reload historical futures data from quandl
            e = engine()
            e.upload_all_quandl_to_db()
        """
        for item in settings.constants.quotes['quandl_commodities_urls']:
            SravzId, url = item
            try:
                if sravzids and SravzId not in sravzids:
                    self.logger.info("Skipped: %s"%(str(item)))
                    continue
                self.logger.info("Processing: %s"%(str(item)))
                self.upload_quandl_to_s3(url, Util.get_hostorical_collection_name_from_sravz_id(SravzId), ndays_back=ndays_back)
            except Exception:
                self.logger.exception('Quandl error: %s'%(str(item)))

    def get_historical_datapoint(self, row_map):
        '''
            Used to process cnbc price and qundl price
        '''
        historical_data = {
                    "Date" : datetime.datetime.strptime(row_map['Date'], '%Y-%m-%d'),
                    "Volume" : helper.util.getfloat(row_map.get("Volume")),
                    "High" : helper.util.getfloat(row_map.get("High")),
                    "Last" : helper.util.getfloat(row_map.get("Last")),
                    "Low" : helper.util.getfloat(row_map.get("Low")),
                    "OpenInterest" : helper.util.getfloat(row_map.get("Open Interest")),
                    "Open" : helper.util.getfloat(row_map.get("Open")),
                    "Change" : helper.util.getfloat(row_map.get("Change")),
                    "Settle" : helper.util.getfloat(row_map.get("Settle"))

        }
        return  historical_data

    def upload_quandl_to_s3(self, url, collection_name, ndays_back = None):
        """
            #Use this function to reload historical futures data from quandl
            from src.util import settings, helper, logger
            from src.services import price
            from src.services.price_helpers.util import Util
            e = price.engine()
            item = settings.constants.quotes['quandl_commodities_urls']
            SravzId, url = item[0]
            collection_name = Util.get_hostorical_collection_name_from_sravz_id(SravzId)
            e.upload_quandl_to_s3(url, Util.get_hostorical_collection_name_from_sravz_id(SravzId))
        """
        we = webcrawler.engine()
        data = we.get_data_from_url(url, return_type="json")
        columnNames = data["dataset"]["column_names"]
        price_data = data["dataset"]["data"]
        # mdbe = mdb.engine(database_name='historical', database_url='historical_url')
        # c_quotes_col = mdbe.get_collection(collection_name)
        # mdbe.create_unique_index_collection([ ("Date", pymongo.ASCENDING)], collection_name, key_name= 'date_unique_index')
        historical_data = []
        for row in price_data:
            row_map = dict(list(zip(columnNames, row)))
            historical_data.append(self.get_historical_datapoint(row_map))
            # if ndays_back and (datetime.datetime.now() - historical_data['Date']).days > ndays_back:
            #     continue
            # c_quotes_col.update_one({"Date": historical_data['Date']}, {"$set": historical_data}, upsert=True)
        self.awse.upload_quotes_to_s3(historical_data, collection_name)

    def get_eodhistoricaldata_live_future_quotes(self, tickers = [], upload_to_db = True):
        mdbe = mdb.engine()
        tickers = tickers or mdbe.get_collection_items(settings.constants.FUTURE_ASSETS_COLLECTION)
        quotes = []
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/real-time/{0}.{1}?api_token={2}&fmt=json".format(ticker['Code'], ticker['Exchange'], settings.constants.EODHISTORICALDATA_API_KEY2)
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
            mdbe = mdb.engine()
            c_quotes_col = mdbe.get_collection("quotes_futures")
            for item in quotes:
                c_quotes_col.update_one({"SravzId": item['SravzId']}, {"$set": item}, upsert=True)

    def get_eodhistoricaldata_historical_future_quotes(self, tickers = [], upload_to_db = True, ndays_back=None):
        '''
            https://eodhistoricaldata.com/api/eod/6A.COMM?api_token=xxxx&order=d&fmt=json
        '''
        e = mdb.engine()
        tickers = e.get_collection_items_fields(settings.constants.FUTURE_ASSETS_COLLECTION, sortDirection = pymongo.ASCENDING)
        for ticker in tickers:
            collection_name = ticker['SravzId'].lower()
            self.logger.info(f"Uploading to collection {collection_name}")
            try:
                url = "https://eodhistoricaldata.com/api/eod/{0}.{1}?api_token={2}&order=d&fmt=json".format(ticker['Code'], ticker['Exchange'], settings.constants.EODHISTORICALDATA_API_KEY2)
                self.logger.info("processing %s" % (url))
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
                    self.logger.info(f"Uploading {len(quotes)} quotes to collection {collection_name}")
                    # self.upload_quotes_to_db(quotes, collection_name=collection_name, ndays_back = ndays_back)
                    self.awse.upload_quotes_to_s3(quotes, collection_name)
            except Exception:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)
