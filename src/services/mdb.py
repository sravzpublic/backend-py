import pymongo, json, pickle
import pandas as pd
import numpy as np
from pymongo import MongoClient
from src.util import settings, helper
from bson import ObjectId
from src.services.cache import Cache

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class engine(object, metaclass=Singleton):
    """description of class"""
    def __init__(self, database_name = 'database', database_url = 'url', db_type = None):
        self.db_type = db_type
        self.database_name = database_name if not db_type else 'historical'
        self.database_url = database_url if not db_type else 'historical_url'
        self.PORTFOLIOS_COLLECTION = 'portfolios'
        self.PORTFOLIO_ASSETS_COLLECTION = 'portfolioassets'
        self.client = None
        self.db = None
        self.db_initialized = False

    def get_client(self):
        if self.client:
            return self.client
        else:
            if settings.constants.development:
                self.client = MongoClient(settings.constants.mongobd_connection_string['dev'][self.database_url])
            else:
                self.client = MongoClient(settings.constants.mongobd_connection_string['prod'][self.database_url])
        return self.client

    def get_database(self):
        if self.db_initialized:
            return self.db
        else:
            if settings.constants.development:
                self.db = self.get_client()[settings.constants.mongobd_connection_string['dev'][self.database_name]]
            else:
                self.db = self.get_client()[settings.constants.mongobd_connection_string['prod'][self.database_name]]
            self.db_initialized = True
        return self.db

    def get_env(self):
        return 'dev' if settings.constants.development else 'prod'

    def save_to_cache(self, collection_name, value):
        cache_key = "%s_%s_%s_%s"%(collection_name, self.database_name, self.db_type, self.get_env())
        Cache.Instance().add(cache_key, value)

    def get_from_cache(self, collection_name):
        cache_key = "%s_%s_%s_%s"%(collection_name, self.database_name, self.db_type, self.get_env())
        return Cache.Instance().get(cache_key)

    def get_collection(self, collection_name):
        if collection_name.isupper():
            raise ValueError('Collection names are all lower case. Check the collection name used')
        return self.get_database()[collection_name]

    def upsert_to_collection(self, collection_name, data, upsert_clause_field = 'SravzId'):
        collection = self.get_collection(collection_name)
        if collection != None:
            for item in data:
                collection.update_one({upsert_clause_field: item[upsert_clause_field]}, {"$set": item}, upsert=True)
        else:
            collection.insert_many(data)

    def create_index_collection(self, collection_name, index_field):
        self.get_collection(collection_name).create_index([(index_field, pymongo.TEXT)], name='sravzid_index', default_language='english')

    def create_unique_index_collection(self, index_fields, collection_name, key_name, unique=True, expireAfterSeconds=None):
        if expireAfterSeconds:
            self.get_collection(collection_name).create_index(index_fields, name=key_name, default_language='english', unique=unique, expireAfterSeconds=expireAfterSeconds)
        else:
            self.get_collection(collection_name).create_index(index_fields, name=key_name, default_language='english', unique=unique)

    def save_collection_to_json(self, collection_name, file_name):
        collection = self.get_collection(collection_name)
        with open(file_name, "w") as f:
            json.dump(JSONEncoder().encode(list(collection.find())), f)

    def get_collection_items(self, collection_name, find_clause = None, iterator=False,
                             sortBy= None, sortDirection = pymongo.ASCENDING,
                             exclude_clause = {}, cache = False, limit = None):
        '''
            limit: number. Limit to number of records
            e = engine()
            e.get_collection_items('portfolioassets', find_clause={"_id": { "$in": [ObjectId('58e131fcfffe0b6bc4926a05')]}}, iterator = False)
            e.get_collection_items('portfolioassets', find_clause={"_id": { "$in": [ObjectId('58e131fcfffe0b6bc4926a05')]}}, iterator = False, cache = True)
            e.get_collection_items('portfolioassets', iterator = False, cache = True)
            e.get_collection_items('portfolioassets', iterator = False, cache = False)
            e.get_collection_items('quotes_commodities', iterator = True, sortBy = 'pricecapturetime', cache = False)
        '''
        if cache:
            items = self.get_from_cache(collection_name)
            if items:
                return items
        collection = self.get_collection(collection_name)
        if not (find_clause or exclude_clause):
            items = list(collection.find()) if not iterator else collection.find()
        else:
            if exclude_clause:
                items = list(collection.find(find_clause, exclude_clause)) if not iterator else collection.find(find_clause, exclude_clause)
            else:
                items = list(collection.find(find_clause)) if not iterator else collection.find(find_clause)
        if sortBy and iterator and sortDirection:
            items = items.sort(sortBy, sortDirection)
        if limit and iterator:
            items = items.limit(limit)
        if cache:
            self.save_to_cache(collection_name, items)
        return items

    def get_collection_items_fields(self, collection_name, find_clause = None, iterator=False,
                             sortBy= None, sortDirection = pymongo.ASCENDING,
                             exclude_clause = {}, field_clause = {}, cache = False):
        '''
            e = engine()
            e.get_collection_items_fields('quotes_stocks', iterator = True, sortDirection = pymongo.ASCENDING, field_clause = {'ticker': 1, '_id': 0})
            e.get_collection_items_fields('quotes_stocks', iterator = True, sortDirection = pymongo.ASCENDING, field_clause = {'ticker': 1, '_id': 0}, cache = True)
            e.get_collection_items_fields('quotes_stocks', iterator = False, sortDirection = pymongo.ASCENDING, cache = True)
        '''
        if cache:
            items = self.get_from_cache(collection_name)
            if items:
                return items
        collection = self.get_collection(collection_name)
        if not (find_clause or exclude_clause or field_clause):
            items = list(collection.find()) if not iterator else collection.find()
        elif (field_clause):
            items = list(collection.find({}, field_clause)) if not iterator else collection.find({}, field_clause)
        else:
            items = list(collection.find(find_clause, exclude_clause, field_clause)) if not iterator else collection.find(find_clause, exclude_clause)
        if sortBy and iterator and sortDirection:
            items = items.sort(sortBy, sortDirection)
        if cache:
            self.save_to_cache(collection_name, items)
        return items

    def get_all_collections_in_db(self):
        '''
            e = engine(db_type = 'historical')
            e.get_all_collections_in_db()
        '''
        return self.get_database().collection_names()

    def rename_collection(self, old_name, new_name):
        '''
            e = engine(db_type = 'historical')
            e.rename_collection('stk_A', 'stk_us_A')
            #[e.rename_collection(name, "stk_us_%s"%(name.split("_")[1])) for name in list(set(e.get_all_collections_in_db()) - set(['stk_us_A']))]
        '''
        return self.get_collection(old_name).rename(new_name)

    def rename_collection_to_lower_case(self, old_name):
        '''
            e = engine(db_type = 'historical')
            #e.rename_collection('stk_A', 'stk_us_A')
            [e.rename_collection_to_lower_case(name) for name in e.get_all_collections_in_db() if 'stk_' in name and name.split('_')[2].isupper()]
            #[e.rename_collection_to_lower_case(name, "stk_us_%s"%(name.split("_")[1])) for name in list(set(e.get_all_collections_in_db()) - set(['stk_us_A']))]
        '''
        return self.get_collection(old_name).rename(old_name.lower())

    def check_collection_exists(self, name):
        '''
            e = engine(db_type = 'historical')
            e.check_collection_exists('stk_us_A')
            e.check_collection_exists('test')
        '''
        return name in self.get_database().collection_names()

    def create_indexes(self):
        '''
            e = engine()
            e.create_indexes()
        '''
        self.get_collection(self.PORTFOLIOS_COLLECTION).create_index(
            [("name", pymongo.ASCENDING), ("user", pymongo.ASCENDING)],
            unique=True
        )

    def get_indexes(self):
        '''
            from src.services import mdb
            e = mdb.engine()
            e.get_indexes()
        '''
        self.get_collection(self.PORTFOLIOS_COLLECTION).index_information()

    def load_csv(self, csv_path, collection_name):
        df = pd.read_csv(csv_path, encoding = 'ISO-8859-1')   # loading csv file
        df['Date'] = df['Date'].astype('datetime64[ns]')
        df.sort_values(by='Date', ascending=False,  inplace=True)
        collection = self.get_collection(collection_name)
        data_dict = df.to_dict('records')
        for row in data_dict:
            if 'Date' in row:
                historical_data = {
                    "Date" : row.get('Date'),
                    "Open" : helper.util.getfloat(row.get("Open")),
                    "High" : helper.util.getfloat(row.get("High")),
                    "Last" : helper.util.getfloat(row.get("Close")),
                    "Low" : helper.util.getfloat(row.get("Low"))
                }
                collection.update_one({"Date": historical_data['Date']}, {"$set": historical_data}, upsert=True)

    def get_collection_as_df(self, collection_name):
        '''
        '''
        cache_key = 'get_collection_as_df%s'%(collection_name)
        value = Cache.Instance().get(cache_key)
        if not value:
            value = self.get_collection_items(collection_name, find_clause = {},
                                            exclude_clause = {'_id': False})
            Cache.Instance().add(cache_key, value)
        return pd.DataFrame(helper.convert(value))
