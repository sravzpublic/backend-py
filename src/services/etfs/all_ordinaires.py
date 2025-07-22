import datetime
from src.util import settings
from src.services import webcrawler
from src.services import mdb


class engine(object):

    def __init__(self):
        pass

    """description of class"""
    def get_xao_components(self, upload_to_db = False):
        '''
            e = engine()
            e.get_xao_components(upload_to_db = True)
        '''
        we = webcrawler.engine()
        components_data = we.get_csv_data_from_url('https://www.allordslist.com/uploads/csv/20190901-all-ords.csv',
        header_location_regex = 'Code,Company,Sector,Market Cap,Weight(%),,Total Index Market Cap,'.encode())
        if upload_to_db and not components_data.empty:
            self.upload_xao_components_to_db(components_data)
        return components_data

    def upload_xao_components_to_db(self, data, collection_name = 'idx_au_xao_components'):
        mdbe = mdb.engine()
        xao_components_col = mdbe.get_collection(collection_name)
        for item in data.to_dict(orient='records'):
            if item:
                item['created'] = datetime.datetime.now(datetime.UTC)
                item['ticker'] = item.pop('Code')
                item['sector'] = item.pop('Sector')
                item['company'] = item.pop('Company')
                item['market_cap'] = item.pop('Market Cap')
                item['weight_pct'] = item.pop('Weight(%)')
                xao_components_col.update_one({"ticker": item['ticker']}, {"$set": item}, upsert=True)

    def get_xao_tickers(self, data, collection_name = 'idx_au_xao_components'):
        mdbe = mdb.engine()
        xao_components_col = mdbe.get_collection(collection_name)
        for item in data:
            if item:
                item = dict((k.lower(), v) for k, v in item.items())
                xao_components_col.update_one({"ticker": item['ticker']}, {"$set": item}, upsert=True)
