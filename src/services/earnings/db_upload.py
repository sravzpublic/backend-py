import  requests, datetime, json, pymongo
import pandas as pd
from src.util import settings, logger
from src.services import webcrawler
from src.services import mdb
from src.services.price_helpers.historical_currency import engine_currency

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        # EOD earning data is available from that day
        d1 = datetime.date(1995, 1, 1)  # start date
        d2 = datetime.datetime.today().date()  # end date
        delta = d2 - d1 # timedelta
        self.ALL_WEEK_DATES = [(d1 + datetime.timedelta(i)) for i in range(delta.days + 1)]
        self.week_start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        self.week_end_dt = self.week_start_dt + datetime.timedelta(days=6)
        delta = self.week_end_dt - self.week_start_dt # timedelta
        # self.WEEK_DATES_STR = [(week_start_dt + datetime.timedelta(i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
        self.WEEK_DATES = [self.week_start_dt + datetime.timedelta(i) for i in range(delta.days + 1)]

    def get_earnings_for_date_range_from_web(self, from_date = datetime.datetime.today(), to_date = datetime.datetime.today(), upload_to_db = False):
        '''
            # Gets data_data cal data from the web
            from src.services.earnings import db_upload
            e = db_upload.engine()
            e.get_earnings_for_date_range_from_web()
            # To load data
            import  requests, datetime, json, pymongo
            import pandas as pd
            from src.util import settings, logger
            from src.services import webcrawler
            from src.services import mdb
            from src.services.price_helpers.historical_currency import engine_currency
            from src.services.earnings import db_upload as earnings_db_upload
            EARNINGS_ENGINE = earnings_db_upload.engine()
            EARNINGS_ENGINE.get_earnings_for_date_range_from_web(upload_to_db = True, from_date = datetime.date(2020,12,1), to_date = datetime.date(2021,1,3))
        '''
        try:
            self.logger.info("Requesting earnings data from {0} - to {1}".format(from_date, to_date))
            we = webcrawler.engine()
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            earnings_url = "https://eodhistoricaldata.com/api/calendar/earnings?api_token={0}&order=d&fmt=json&from={1}&to={2}".format(
                settings.constants.EODHISTORICALDATA_API_KEY,
                from_date_str,
                to_date_str)
            earnings_data = we.get_data_from_url(earnings_url, return_type = 'json')
            if upload_to_db and earnings_data:
                self.upload_earnings_to_db(earnings_data)
            return earnings_data
        except:
            self.logger.exception("Could not get earning data for dates: {0} to {1}".format(from_date, to_date))


    def get_current_week_earnings_from_mdb(self, collection_name = 'earnings'):
        mdbe = mdb.engine()
        start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        end_dt = start_dt + datetime.timedelta(days=6)
        earnings_col = mdbe.get_collection(collection_name)
        return earnings_col.find({'date' : {'$gte': datetime.datetime.combine(start_dt, datetime.datetime.min.time()),
                                               '$lt': datetime.datetime.combine(end_dt, datetime.datetime.min.time())}})

    def upload_earnings_to_db(self, earnings_data, collection_name = 'earnings'):
        if earnings_data and 'earnings' in earnings_data:
            mdbe = mdb.engine()
            earnings_col = mdbe.get_collection(collection_name)
            for item in earnings_data.get('earnings'):
                item['report_date'] =  datetime.datetime.strptime(item['report_date'], '%Y-%m-%d')
                item['date'] =  datetime.datetime.strptime(item['date'], '%Y-%m-%d')
                try:
                    earnings_col.update_one({
                        "code": item['code'],
                        "report_date": item['report_date'],
                        "date": item['date']}, {"$set": item}, upsert=True)
                except:
                    self.logger.error("Could not upload earnings item: {0}".format(item), exc_info=True)
        else:
            self.logger.exception("Earnings data empty, nothing to upload to db: {0}".format(earnings_data))

    def get_all_weeks_earnings_from_web(self, upload_to_db = False):
        '''
            # Use this to upload for all week since 1995-01-01
            from src.services.earnings import db_upload
            e = db_upload.engine()
            e.get_all_weeks_earnings_from_web(upload_to_db = True)
        '''
        for data_date in self.ALL_WEEK_DATES:
            self.get_earnings_for_date_range_from_web(from_date = data_date,
            to_date = data_date,
            upload_to_db = upload_to_db)

    def get_current_week_earnings_from_web(self, upload_to_db = False):
        '''
            # Use this to upload current week's earnings from the web
            from src.services.earnings import db_upload
            e = db_upload.engine()
            e.get_current_week_earnings_from_web(upload_to_db = True)
        '''
        #for data_date in self.WEEK_DATES:
        week_start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        week_end_dt = week_start_dt + datetime.timedelta(days=6)
        self.get_earnings_for_date_range_from_web(from_date = week_start_dt,
        to_date = week_end_dt,
        upload_to_db = upload_to_db)

