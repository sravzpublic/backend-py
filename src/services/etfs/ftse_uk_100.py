import datetime
from src.util import settings
from src.services import webcrawler
from src.services import mdb


class engine(object):

    def __init__(self):
        pass

    """description of class"""
    def get_ftse_uk_100_components(self, upload_to_db = False):
        '''
            e = engine()
            e.get_dj30_components(upload_to_db = True)
        '''
        we = webcrawler.engine()
        tables = we.get_html_tables(None, settings.constants.idx_uk_ftse['components_url'], settings.constants.idx_uk_ftse['table_class'], None)
        components_data = we.get_data_from_html_table_ignore_missing_tags(tables[0], th_is_present_thead_absent = True)
        if upload_to_db and components_data:
            self.upload_ftse_uk_100_components_to_db(components_data)
        return components_data

    def upload_ftse_uk_100_components_to_db(self, data, collection_name = 'idx_uk_ftse_components'):
        mdbe = mdb.engine()
        ftse_uk_100_components_col = mdbe.get_collection(collection_name)
        for item in data:
            if item:
                item = dict((k.lower(), v) for k, v in item.items())
                item['created'] = datetime.datetime.now(datetime.UTC)
                item['sector'] = item.pop('ftseindustryclassificationbenchmarksector[9]')
                ftse_uk_100_components_col.update_one({"ticker": item['ticker']}, {"$set": item}, upsert=True)

