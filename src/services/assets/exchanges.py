#!/usr/bin/env python
import json, datetime, pycountry, os
from src.services import mdb, aws
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings, logger, helper
from src.services.cache import Cache
import pandas as pd

package_directory = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(package_directory, '..', '..','..','data', 'exchanges.json')
world_locations = os.path.join(package_directory, '..', '..','..','data', 'worldlocations.json')
world_capitals = os.path.join(package_directory, '..', '..','..','data', 'world_capitals.json')
world_major_indices = os.path.join(package_directory, '..', '..','..','data', 'major_indices.csv')
commodidies_list = os.path.join(package_directory, '..', '..','..','data', 'eod_commodities.csv')
options_tickers = os.path.join(package_directory, '..', '..','..','data', 'eod_options_tickers.csv')
mdbe = mdb.engine()
eode = eodhistoricaldata.engine()
awse = aws.engine()
logger = logger.RotatingLogger(__name__).getLogger()

def upload_assets():
    mdbe = mdb.engine()
    exchange_assets = []
    with open(data_file) as f:
        data = json.load(f)
        for exchange_asset in data:
            if exchange_asset["MIC"]:
                exchange_asset["SravzId"] = "exchange_{0}_{1}".format(exchange_asset["MIC"], exchange_asset["Exchange Name"].replace(' Exchange', '')).lower().replace(',','_').replace(' ','_').replace('__','_')
                exchange_asset["Ticker"] = exchange_asset["MIC"].lower().replace(',','').replace(' ','_')
                exchange_asset["Code"] = exchange_asset["Exchange Code"]
                exchange_asset["Name"] = exchange_asset["Exchange Name"]
                exchange_assets.append(exchange_asset)
        mdbe.upsert_to_collection(settings.constants.EXCHANGE_ASSETS_COLLECTION, exchange_assets)
        mdbe.create_index_collection(settings.constants.EXCHANGE_ASSETS_COLLECTION, "SravzId")

def upload_world_locations():
    with open(world_locations) as f:
        mdbe.upsert_to_collection(settings.constants.WORLD_LOCATIONS_COLLECTION, json.load(f), upsert_clause_field='name')

def upload_option_tickers():
    df = pd.read_csv(options_tickers, encoding = 'ISO-8859-1')   # loading csv file
    df['Ticker'] = df['Code']
    df['Country'] = 'US'
    df['SravzId'] = df.apply(lambda row: f"opt_{row.Code.lower()}_{row.Country.lower()}" , axis=1)
    df['Exchange'] = df.apply(lambda row: "INDX" if row.Code in ["VIX", "GSPC", "RUT", "NDX", "DJI", "SP100"] else "US", axis=1)
    collection = mdbe.get_collection(settings.constants.OPTION_ASSETS_COLLECTION)
    data_dict = df.to_dict('records')
    for row in data_dict:
        collection.update_one({"Code": row['Code']}, {"$set": row}, upsert=True)

def upload_world_capitals():
    with open(world_capitals) as f:
        data = json.load(f)
        for world_capital in data:
            world_capital["CapitalLatitude"] = helper.util.getfloat(world_capital["CapitalLatitude"])
            world_capital["CapitalLongitude"] = helper.util.getfloat(world_capital["CapitalLongitude"])
        mdbe.upsert_to_collection(settings.constants.WORLD_CAPITALS_COLLECTION, data, upsert_clause_field='CountryName')

def upload_world_major_indices_names():
    df = pd.read_csv(world_major_indices, encoding = 'ISO-8859-1')   # loading csv file
    collection = mdbe.get_collection(settings.constants.WORLD_MAJOR_INDICES_COLLECTION)
    data_dict = df.to_dict('records')
    for row in data_dict:
        collection.update_one({"IndexName": row['IndexName']}, {"$set": row}, upsert=True)

def upload_etfs_list():
    df = pd.read_csv(settings.constants.EOD_ETF_LIST_URL, encoding = 'ISO-8859-1')   # loading csv file
    collection = mdbe.get_collection(settings.constants.ETF_ASSETS_COLLECTION)
    column_names = {}
    [column_names.update({x:x.replace(' ','')}) for x in df.columns]
    df = df.rename(columns=column_names)
    df = df[df['Country'] == "USA"]
    data_dict = df.to_dict('records')
    for row in data_dict:
        try:
            country = pycountry.countries.get(name=row['Country'])
            if not country:
                country = pycountry.countries.get(alpha_2=row['Country'])
            if not country:
                country = pycountry.countries.get(alpha_3=row['Country'])
            if country:
                row['SravzId'] = 'etf_{0}_{1}'.format(country.alpha_2.lower(), row['ETFCode']).lower()
            else:
                row['SravzId'] = 'etf_{0}_{1}'.format(row['Country'], row['ETFCode']).lower()
            collection.update_one({"ETFCode": row['ETFCode']}, {"$set": row}, upsert=True)
        except:
            logger.exception("Unable to process {0}".format(row))

def upload_exchange_symbol_list():
    '''
        Uploads symblols of all exchanges
        from src.services.assets.exchanges import upload_exchange_symbol_list
    '''
    # Collection that stores symbols for all world exchanges
    collection = mdbe.get_collection(settings.constants.EXCHANGE_SYMBOLS_COLLECTION)
    # Collection contains list of all world exchanges
    for exchange_asset in mdbe.get_collection_items(settings.constants.EXCHANGE_ASSETS_COLLECTION):
        # Do not process not US exchange
        if exchange_asset['Exchange Code'] != "US":
            pass        
        logger.info("Processing exchange {0}".format(exchange_asset))
        try:
            # Get all the symbols traded at the exchange
            exchange_symbols = eode.get_exchange_symbols(exchange_asset['Exchange Code'])
            if exchange_symbols:
                for row in exchange_symbols:
                    try:
                        country = pycountry.countries.get(name=row['Country'])
                        if not country:
                            country = pycountry.countries.get(alpha_2=row['Country'])
                        if not country:
                            country = pycountry.countries.get(alpha_3=row['Country'])
                        if country:
                            row['SravzId'] = '{0}_{1}_{2}'.format(row['Type'].replace(" ",''), country.alpha_2.lower(), row['Code']).lower()
                            row['APICode'] = "{0}.{1}".format(row.get('Code'), country.alpha_2.upper())
                        else:
                            row['SravzId'] = '{0}_{1}_{2}'.format(row['Type'].replace(" ",''), row['Country'], row['Code']).lower()
                            row['APICode'] = "{0}.{1}".format(row.get('Code'), row['Country'])
                        # We are interested in USA exchange only
                        if row['Country'] == "USA": # Upload USA tickers only
                            collection.update_one({"SravzId": row['SravzId']}, {"$set": row}, upsert=True)
                    except:
                        logger.exception("Unable to process {0}".format(row))
        except Exception as e:
            logger.exception("Error upload exchange symbols for exchange_asset {0} {1}".format(exchange_asset, e))

def upload_exchange_components_to_s3():
    for exchange_asset in mdbe.get_collection_items(settings.constants.EXCHANGE_ASSETS_COLLECTION):
        try:
            awse.upload_to_bucket(settings.constants.SRAVZ_DATA_S3_BUCKET,
            "{0}{1}".format(settings.constants.SRAVZ_DATA_EOD_EXCHANGE_COMPONENTS_PREFIX, exchange_asset['SravzId']),
            json.dumps(eode.get_exchange_components(exchange_asset['Exchange Code'])),
            expires=None, gzip_data=True)
        except:
            logger.exception("Error upload exchange_asset {0}".format(exchange_asset))

def upload_exchange_components_to_mdb():
    exchange_assets_components_collection = mdbe.get_collection(settings.constants.EXCHANGE_ASSETS_COMPONENTS_COLLECTION)
    for exchange_asset in mdbe.get_collection_items(settings.constants.EXCHANGE_ASSETS_COLLECTION):
        try:
            cache_key = 'upload_exchange_components_to_mdb_%s'%(exchange_asset['SravzId'])
            value = Cache.Instance().get(cache_key)
            if (type(value) == pd.core.frame.DataFrame and value.empty) or (value is None):
                data = json.loads(awse.download_object(settings.constants.SRAVZ_DATA_S3_BUCKET,
                "{0}{1}".format(settings.constants.SRAVZ_DATA_EOD_EXCHANGE_COMPONENTS_PREFIX,
                exchange_asset['SravzId']),
                gzip_data = True))
                if data:
                    for component in data:
                        component['ExchangeSravzId'] = exchange_asset['SravzId']
                        component['SravzId'] = "{0}_{1}_{2}".format(component['Type'].replace('Common Stock','stk'), component['Country'], component['Code']).lower()
                        exchange_assets_components_collection.update_one({"SravzId": component['SravzId'], "Code": component["Code"]}, {"$set": component}, upsert=True)
                    Cache.Instance().add(cache_key, data)
                    logger.info("Exchange components {0} uploaded to mdb".format(exchange_asset['SravzId']))
                else:
                    logger.info("Exchange components not found for {0}".format(exchange_asset['SravzId']))
        except:
            logger.exception("Error upload exchange_asset {0}".format(exchange_asset))

def upload_futures_list_to_mdb():
    url = "https://eodhistoricaldata.com/api/exchange-symbol-list/COMM?api_token={0}".format(settings.constants.EODHISTORICALDATA_API_KEY)
    df = pd.read_csv(url, encoding = 'ISO-8859-1')   # loading csv file
    collection = mdbe.get_collection(settings.constants.FUTURE_ASSETS_COLLECTION)
    data_dict = df.to_dict('records')
    for row in data_dict:
        try:
            country = pycountry.countries.get(name=row['Country'])
            if not country:
                country = pycountry.countries.get(alpha_2=row['Country'])
            if not country:
                country = pycountry.countries.get(alpha_3=row['Country'])
            if country:
                row['SravzId'] = '{0}_{1}_{2}'.format(row['Type'].replace(" ",''), country.alpha_2.lower(), row['Code']).lower()
                row['APICode'] = "{0}.{1}".format(row.get('Code'), country.alpha_2.upper())
            else:
                row['SravzId'] = '{0}_{1}_{2}'.format(row['Type'].replace(" ",''), row['Country'], row['Code']).lower()
                row['APICode'] = "{0}.{1}".format(row.get('Code'), row['Country'])
            collection.update_one({"SravzId": row['SravzId']}, {"$set": row}, upsert=True)
        except:
            logger.exception("Unable to process {0}".format(row))

