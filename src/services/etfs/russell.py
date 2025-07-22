import datetime
from src.util import settings
from src.services import webcrawler
from src.services import mdb


class engine(object):

    def __init__(self):
        pass

    """description of class"""
    def get_russell_components(self, upload_to_db = False):
        '''
            e = engine()
            e.get_russell_components(upload_to_db = True)
        '''
        we = webcrawler.engine()
        russell_data = we.get_csv_data_from_url(settings.constants.russle3000['components_url'], b'Ticker,Name')
        russell_data = russell_data.rename(index=str, columns =
            {'Ticker': 'ticker',
             'Name': 'name',
             'Asset Class': 'asset_class',
             'Weight (%)': 'weight_pct',
             'Price': 'price',
             'Shares': 'shares',
             'Market Value': 'market_value',
             'Notional Value': 'notional_value',
             'Sector': 'sector',
             'SEDOL': 'sedol',
             'ISIN': 'isin',
             'Exchange': 'exchange'
             })
        if upload_to_db and not russell_data.empty:
            self.upload_russell_components_to_db(russell_data.to_dict('records'))
        return russell_data

    def upload_russell_components_to_db(self, data, collection_name = 'idx_us_rua_components'):
        mdbe = mdb.engine()
        russell_components_col = mdbe.get_collection(collection_name)
        for item in data:
            if item:
                item['Created'] = datetime.datetime.now(datetime.UTC)
                russell_components_col.update_one({"ticker": item['ticker']}, {"$set": item}, upsert=True)

