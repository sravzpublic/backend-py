from src.services import price
from src.util.settings import constants
def upload(sravzids = None):
    '''
        To upload all historical data to mongodb. Use with fresh mongodb instances or irregular updates to data
    '''
    e = price.engine()
    e.get_eodhistoricaldata_historical_future_quotes()

if __name__ == '__main__':
    upload()

