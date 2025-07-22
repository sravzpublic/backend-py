import datetime, json
from src.util import settings, logger
from src.services import webcrawler
from src.services import mdb


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    """description of class"""
    def get_russell_components(self, upload_to_db = False):
        '''
            e = engine()
            e.get_russell_components(upload_to_db = True)
        '''
        we = webcrawler.engine()
        russell_data = json.loads(we.get_data_from_url(settings.constants.russle2000['components_url'])[1:])
        if upload_to_db and russell_data:
            self.upload_russell_components_to_db(russell_data)
        return russell_data

    def upload_russell_components_to_db(self, data, collection_name = 'idx_us_rut_components'):
        mdbe = mdb.engine()
        russell_components_col = mdbe.get_collection(collection_name)
        for item in data.get('aaData'):
            if item:
                try:
                    component = {
                        "ticker" : item[0],
                        "sector" : item[8],
                        "company" : item[1],
                        "market_cap" : item[6]['raw'],
                        "weight_pct" : item[3]['raw']
                    }
                    component['Created'] = datetime.datetime.now(datetime.UTC)
                    russell_components_col.update_one({"ticker": component['ticker']}, {"$set": component}, upsert=True)
                except:
                    self.logger.error("Could not process component {0}".format(item), exc_info=True)
