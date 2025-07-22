import  requests, datetime, json, pymongo
import pandas as pd
from src.util import settings, helper, logger
from src.services import webcrawler, aws, mdb
from src.services import idgenerator
from src.services.price_helpers.historical_currency import engine_currency
from src.services.price_helpers import util
from titlecase import titlecase
from src.services.price_helpers.util import Util


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()


    def get_historical_datapoint(self, row_map, collection_name):
        if collection_name == 'treasury_real_longterm_rate':
            historical_data = {
                        "Date" : datetime.datetime.strptime(row_map['Date'], '%Y-%m-%d'),
                        "LongTermRealAverage" : helper.util.getfloat(row_map.get("LT Real Average (\u003e10Yrs)"))
            }
        elif collection_name == 'treasury_real_yieldcurve_rate':
            #"Date","5 YR","7 YR","10 YR","20 YR","30 YR"
            historical_data = {
                        "Date" : datetime.datetime.strptime(row_map['Date'], '%Y-%m-%d'),
                        "5YR" : helper.util.getfloat(row_map.get("5 YR")),
                        "7YR" : helper.util.getfloat(row_map.get("7 YR")),
                        "10YR" : helper.util.getfloat(row_map.get("10 YR")),
                        "20YR" : helper.util.getfloat(row_map.get("20 YR")),
                        "30YR" : helper.util.getfloat(row_map.get("30 YR")),
            }
        elif collection_name == 'treasury_bill_rate':
            #"Date","4 Wk Bank Discount Rate","4 Wk Coupon Equiv","13 Wk Bank Discount Rate",
            #"13 Wk Coupon Equiv","26 Wk Bank Discount Rate","26 Wk Coupon Equiv",
            #"52 Wk Bank Discount Rate","52 Wk Coupon Equiv"
            historical_data = {
                        "Date" : datetime.datetime.strptime(row_map['Date'], '%Y-%m-%d'),
                        "4WkBankDiscountRate" : helper.util.getfloat(row_map.get("4 Wk Bank Discount Rate")),
                        "4WkCouponEquiv" : helper.util.getfloat(row_map.get("4 Wk Coupon Equiv")),
                        "13WkBankDiscountRate" : helper.util.getfloat(row_map.get("13 Wk Bank Discount Rate")),
                        "13WkCouponEquiv" : helper.util.getfloat(row_map.get("13 Wk Coupon Equiv")),
                        "26WkBankDiscountRate" : helper.util.getfloat(row_map.get("26 Wk Bank Discount Rate")),
                        "26WkCouponEquiv" : helper.util.getfloat(row_map.get("26 Wk Coupon Equiv")),
                        "52WkBankDiscountRate" : helper.util.getfloat(row_map.get("52 Wk Bank Discount Rate")),
                        "52WkCouponEquiv" : helper.util.getfloat(row_map.get("52 Wk Coupon Equiv"))
            }
        elif collection_name == 'treasury_long_term_rate':
            #"Date","LT Composite \u003e 10 Yrs","Treasury 20-Yr CMT","Extrapolation Factor"
            historical_data = {
                        "Date" : datetime.datetime.strptime(row_map['Date'], '%Y-%m-%d'),
                        "LTComposite10Yrs" : helper.util.getfloat(row_map.get("LT Composite \u003e 10 Yrs")),
                        "Treasury20-YrCMT" : helper.util.getfloat(row_map.get("Treasury 20-Yr CMT")),
                        "Extrapolation Factor" : row_map.get("Extrapolation Factor")
            }
        return  historical_data

    def upload_quandl_to_s3(self, url, collection_name):
        """
            #Use this function to reload historical futures data from quandl
            from src.util import settings, helper, logger
            from src.services import price
            from src.services.price_helpers.util import Util
            e = price.engine()
            item = settings.constants.quotes['quandl_commodities_urls']
            SravzId, url = item[0]
            collection_name = Util.get_hostorical_collection_name_from_sravz_id(SravzId)
            e.upload_quandl_to_s3(url, Util.get_hostorical_collection_name_from_sravz_id(SravzId))
        """
        we = webcrawler.engine()
        data = we.get_data_from_url(url, return_type="json")
        columnNames = data["dataset"]["column_names"]
        price_data = data["dataset"]["data"]
        #mdbe = mdb.engine(database_name='historical', database_url='historical_url')
        #c_quotes_col = mdbe.get_collection(collection_name)
        #mdbe.create_unique_index_collection([ ("Date", pymongo.ASCENDING)], collection_name, key_name= 'date_unique_index')
        quotes = []
        for row in price_data:
            quotes.append(self.get_historical_datapoint(dict(list(zip(columnNames, row))), collection_name))
            # historical_data =
            # c_quotes_col.update_one({"Date": historical_data['Date']}, {"$set": historical_data}, upsert=True)
        self.awse.upload_quotes_to_s3(quotes, collection_name)

