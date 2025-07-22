import  requests, datetime, json, pymongo
import pandas as pd
from src.util import settings, helper, logger
from src.services import webcrawler
from src.services import mdb
from src.services import idgenerator
from src.services.price_helpers.historical_currency import engine_currency
from src.services.price_helpers import util
from titlecase import titlecase
from src.services.price_helpers.util import Util


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    """description of class"""
    def upload_quandl_nahb_int_forecast_to_db(self, ):
        """
            #Use this function to reload history nahb interest rates from quandl
            e = engine()
            e.upload_quandl_nahb_to_db()
        """
        self.upload_quandl_to_s3(settings.constants.quotes['int_nahb_forecast'],
        Util.get_hostorical_collection_name_from_sravz_id('int_nahb_forecast'))

    def get_historical_datapoint(self, row_map):
        historical_data = {
                    "Date" : datetime.datetime.strptime(row_map['Year'], '%Y-%m-%d'),
                    "FederalFundsRate" : helper.util.getfloat(row_map.get("Federal Funds Rate")),
                    "90dayTBillRate" : helper.util.getfloat(row_map.get("Hi90 day T Bill Rategh")),
                    "OneYearMaturityTreasuryYield" : helper.util.getfloat(row_map.get("One Year Maturity Treasury Yield")),
                    "TenYearMaturityTreasuryYield" : helper.util.getfloat(row_map.get("Ten Year Maturity Treasury Yield")),
                    "FreddieMacCommitmentFixedRateMortgages" : helper.util.getfloat(row_map.get("Freddie Mac Commitment Fixed Rate Mortgages")),
                    "FreddieMacCommitmentARMs" : helper.util.getfloat(row_map.get("Freddie Mac Commitment ARMs")),
                    "PrimeRate" : helper.util.getfloat(row_map.get("Prime Rate"))
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
        mdbe = mdb.engine(database_name='historical', database_url='historical_url')
        c_quotes_col = mdbe.get_collection(collection_name)
        mdbe.create_unique_index_collection([ ("Date", pymongo.ASCENDING)], collection_name, key_name= 'date_unique_index')
        for row in price_data:
            row_map = dict(list(zip(columnNames, row)))
            historical_data = self.get_historical_datapoint(row_map)
            c_quotes_col.update_one({"Date": historical_data['Date']}, {"$set": historical_data}, upsert=True)


