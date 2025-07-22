import  datetime
from src.util import settings, logger
from src.services import webcrawler
from src.services import mdb

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    def get_economic_events_for_date_range_from_web(self, from_date = datetime.datetime.today(), to_date = datetime.datetime.today(), upload_to_db = False):
        '''
            # Gets data_data cal data from the web
            from src.services.economic_events import db_upload
            e = db_upload.engine()
            e.get_economic_events_for_date_range_from_web()
            # To load data
            import  requests, datetime, json, pymongo
            import pandas as pd
            from src.util import settings, logger
            from src.services import webcrawler
            from src.services import mdb
            from src.services.price_helpers.historical_currency import engine_currency
            from src.services.economic_events import db_upload as economic_events_db_upload
            EARNINGS_ENGINE = economic_events_db_upload.engine()
            EARNINGS_ENGINE.get_economic_events_for_date_range_from_web(upload_to_db = True, from_date = datetime.date(2020,12,1), to_date = datetime.date(2021,1,3))
        '''
        try:
            self.logger.info("Requesting economic_events data from {0} - to {1}".format(from_date, to_date))
            we = webcrawler.engine()
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            economic_events_url = "https://eodhistoricaldata.com/api/economic-events?api_token={0}&order=d&fmt=json&from={1}&to={2}&limit=1000".format(
                settings.constants.EODHISTORICALDATA_API_KEY,
                from_date_str,
                to_date_str)
            economic_events_data = we.get_data_from_url(economic_events_url, return_type = 'json')
            if upload_to_db and economic_events_data:
                self.upload_economic_events_to_db(economic_events_data)
            return economic_events_data
        except:
            self.logger.exception("Could not get economic_events data for dates: {0} to {1}".format(from_date, to_date))


    def get_current_week_economic_events_from_mdb(self, collection_name = 'economic_events'):
        mdbe = mdb.engine()
        start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        end_dt = start_dt + datetime.timedelta(days=6)
        economic_events_col = mdbe.get_collection(collection_name)
        return economic_events_col.find({'date' : {'$gte': datetime.datetime.combine(start_dt, datetime.datetime.min.time()),
                                               '$lt': datetime.datetime.combine(end_dt, datetime.datetime.min.time())}})

    def upload_economic_events_to_db(self, economic_events_data, collection_name = 'economic_events'):
        if economic_events_data:
            mdbe = mdb.engine()
            economic_events_col = mdbe.get_collection(collection_name)
            for item in economic_events_data:
                item['date'] =  datetime.datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
                try:
                    economic_events_col.update_one({
                        "type": item['type'],
                        "date": item['date']}, {"$set": item}, upsert=True)
                except:
                    self.logger.error("Could not upload economic_events item: {0}".format(item), exc_info=True)
            self.logger.info("Upserted: {0} economic_events items".format(len(economic_events_data)))
        else:
            self.logger.exception("Economics events data empty, nothing to upload to db: {0}".format(economic_events_data))


    def get_current_week_economic_events_from_web(self, upload_to_db = False):
        '''
            # Use this to upload current week's economic_events from the web
            from src.services.economic_events import db_upload
            e = db_upload.engine()
            e.get_current_week_economic_events_from_web(upload_to_db = True)
        '''
        #for data_date in self.WEEK_DATES:
        week_start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        week_end_dt = week_start_dt + datetime.timedelta(days=6)
        self.get_economic_events_for_date_range_from_web(from_date = week_start_dt,
        to_date = week_end_dt,
        upload_to_db = upload_to_db)

