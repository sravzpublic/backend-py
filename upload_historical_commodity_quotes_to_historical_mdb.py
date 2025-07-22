from src.services import price
from src.util.settings import constants
def upload_all_historical_data(sravzids = None):
    '''
        To upload all historical data to mongodb. Use with fresh mongodb instances or irregular updates to data
    '''
    e = price.engine()
    e.upload_all_quandl_to_db(sravzids = sravzids, ndays_back=constants.NDAY_BACK_FOR_HISTORICAL_QUOTES)

if __name__ == '__main__':
    upload_all_historical_data()

