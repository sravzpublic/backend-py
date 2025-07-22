import  requests, datetime, json, pymongo
import pandas as pd
from src.util import settings, logger
from src.services import webcrawler
from src.services import mdb
from src.services.price_helpers.historical_currency import engine_currency

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        #xrange does not include the last integer
        #self.CAL_DATES = [(year, format(week, '02'))
        #             for year in range(2001, datetime.datetime.now().isocalendar()[0] + 1)
        #             for week in range(1, datetime.date(year, 12, 28).isocalendar()[1] + 1)]
        d1 = datetime.date(2001, 1, 1)  # start date
        d2 = datetime.datetime.today().date()  # end date
        delta = d2 - d1 # timedelta
        self.CAL_DATES = [(d1 + datetime.timedelta(i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
        week_start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        week_end_dt = week_start_dt + datetime.timedelta(days=6)
        delta = week_end_dt - week_start_dt # timedelta
        self.WEEK_DATES = [(week_start_dt + datetime.timedelta(i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]


    def get_day_eco_cal_from_web_for_day_range(self, upload_to_db = False, from_date = None, end_date = None):
        '''
            # To upload ecocal in a date range
            from src.services.ecocal import engine
            e = engine()
            import datetime
            e.get_day_eco_cal_from_web_for_day_range(upload_to_db = True, from_date = datetime.date(2015,9,12), end_date = datetime.date(2019,5,30))
            e.get_day_eco_cal_from_web(upload_to_db = True)
        '''
        if from_date and end_date:
            delta = end_date - from_date
            for i in range(delta.days + 1):
                data_date = (from_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                try:
                    self.logger.info("Processing data date: {0}".format(data_date))
                    self.get_eco_cal_from_web_by_date(upload_to_db = upload_to_db, data_date = data_date)
                except:
                    self.logger.exception("Cannot get data for data_data: {0}".format(data_date))

    def get_eco_cal_from_web_by_date(self, upload_to_db = False, data_date = None):
        '''
            Gets data_data cal data from the web
            data_date should be in strftime("%Y-%m-%d")
        '''
        try:
            self.logger.info("Processing data date: {0}".format(data_date))
            we = webcrawler.engine()
            data_date = data_date or datetime.datetime.today().strftime("%Y-%m-%d")
            eco_cal_url = "{0}{1}".format(settings.constants.YAHOO_ECO_CAL_BASE_URL, data_date)
            html_data = we.get_data_from_url(eco_cal_url)
            tables = we.get_html_tables(html_data, table_class = "W(100%)")
            day_data = we.get_data_from_html_table_ignore_missing_tags(tables[0], first_row_is_header_row = True)
            if upload_to_db and day_data:
                self.upload_raw_data_from_web_to_mdb(day_data, data_date)
            return day_data
        except:
            self.logger.exception("Cannot get data for data_data: {0}".format(data_date))


    def get_current_week_eco_cal_from_mdb(self,collection_name = 'economic_calendar'):
        mdbe = mdb.engine()
        start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        end_dt = start_dt + datetime.timedelta(days=6)
        economic_calendar_col = mdbe.get_collection(collection_name)
        return economic_calendar_col.find({'date' : {'$gte': datetime.datetime.combine(start_dt, datetime.datetime.min.time()),
                                               '$lt': datetime.datetime.combine(end_dt, datetime.datetime.min.time())}})

    def upload_raw_data_from_web_to_mdb(self, week_data, data_date):
        data = []
        for day_data in week_data:
            day_data['FullDate'] = data_date
            data.append(day_data)
        if data:
            self.upload_eco_cal_to_db(data, 'economic_calendar')

    def get_all_weeks_eco_cal_from_web(self, upload_to_db = False):
        '''
            Use this to upload for all week since 2001-01-01
        '''
        for data_date in self.CAL_DATES:
            self.get_eco_cal_from_web_by_date(upload_to_db = upload_to_db, data_date = data_date)

    def get_current_week_eco_cal_from_web(self, upload_to_db = False):
        '''
            Use this to upload current week's eco cal from the web
        '''
        # Calculate dates here, else nsq workers use stale dates
        week_start_dt = datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())
        week_end_dt = week_start_dt + datetime.timedelta(days=6)
        delta = week_end_dt - week_start_dt # timedelta
        WEEK_DATES = [(week_start_dt + datetime.timedelta(i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
        for data_date in WEEK_DATES:
            self.get_eco_cal_from_web_by_date(upload_to_db = upload_to_db, data_date = data_date)

    def upload_eco_cal_to_db(self, data, collection_name = 'economic_calendar'):
        mdbe = mdb.engine()
        economic_calendar_col = mdbe.get_collection(collection_name)
        for item in data:
            try:
                #Update date in date format instead of string format, Mongoose expects date format
                item['Date'] = datetime.datetime.strptime(item.pop('FullDate'),'%Y-%m-%d') #item.pop('FullDate') datetime.datetime.now().strftime('%Y-%m-%d'),
                item = dict((k.lower(), v) for k, v in item.items())
                economic_calendar_col.update_one({"date": item['date'], "event" : item['event'], "country" : item["country"], "eventtime" : item["eventtime"] },
                {"$set": item}, upsert=True)
            except:
                self.logger.error("Could not upload eco-cal item: {0}".format(item), exc_info=True)


