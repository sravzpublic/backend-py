import datetime
from src.util import settings, logger
from src.services import webcrawler
from src.services import mdb


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    """description of class"""
    def get_snp_components(self, upload_to_db = False):
        '''
            e = engine()
            e.get_snp_components(upload_to_db = True)
        '''
        we = webcrawler.engine()
        tables = we.get_html_tables(None, settings.constants.snp['components_url'], settings.constants.snp['table_class'], None)
        components_data = we.get_data_from_html_table_ignore_missing_tags(tables[0], th_is_present_thead_absent = True)
        if upload_to_db and components_data:
            self.upload_snp_components_to_db(components_data)
        return components_data

    def upload_snp_components_to_db(self, data, collection_name = 'idx_us_gspc_components'):
        mdbe = mdb.engine()
        snp_components_col = mdbe.get_collection(collection_name)
        for item in data:
            if item:
                item = dict((k.lower(), v) for k, v in item.items())
                if (item['datefirstadded']):
                    try:
                        item['datefirstadded'] = datetime.datetime.strptime(item.pop('datefirstadded'),'%Y-%m-%d')
                    except Exception:
                        item['datefirstadded'] = None
                        self.logger.error('Could not determine datafirstadded for: {0}'.format(item['symbol']), exc_info=True)
                else:
                    item['datefirstadded'] = None
                item['created'] = datetime.datetime.now(datetime.UTC)
                item['sector'] = item.pop('gicssector')
                item['ticker'] = item['symbol']
                snp_components_col.update_one({"symbol": item['ticker']}, {"$set": item}, upsert=True)
        self.logger.info('Uploaded {0} SNP Components to database'.format(len(data)))

