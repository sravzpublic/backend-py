from src.util import settings, logger, helper, country_currency_mapping
from fredapi import Fred
from src.services import mdb
import datetime
import requests
import pycountry
from src.services import webcrawler
from bs4 import BeautifulSoup
import pandas as pd


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()

    def get_historical_crypto_hash_rate(self, upload_to_db=False, ndays_back=None):
        data = self.we.get_csv_data_from_url(url=settings.constants.BITCOIN_HASH_RATE_URL)
        # Convert TH to GH
        data.columns = ['Date', 'HashRateGH']
        data['Date'] =  pd.to_datetime(data['Date'], format='%Y-%m-%d %H:%M:%S')
        data['HashRateGH'] = data['HashRateGH'] * 1000
        if upload_to_db:
            self.upload_hash_rate_to_db(data, collection_name='crypto_btc_usd_hash_rate')

        data = self.we.get_csv_data_from_url(url=settings.constants.ETHEREUM_HASH_RATE_URL)
        #data = pd.read_csv('/tmp/hash.csv')
        data.columns = ['Date', 'Timestamp', 'HashRateGH']
        data['Date'] =  pd.to_datetime(data['Date'], format='%m/%d/%Y')
        data = data.drop(['Timestamp'], axis=1)
        if upload_to_db:
            self.upload_hash_rate_to_db(data, collection_name='crypto_eth_usd_hash_rate')


    def upload_hash_rate_to_db(self, data, collection_name, ndays_back=None):
        mdbe_historical = mdb.engine(database_name='historical', database_url='historical_url')
        hash_rate_col = mdbe_historical.get_collection(collection_name)
        for item in data.to_dict('records'):
            if ndays_back and (datetime.datetime.now() - item['Date']).days > ndays_back:
                continue
            hash_rate_col.update_one({"Date": item['Date']}, {"$set": item}, upsert=True)

