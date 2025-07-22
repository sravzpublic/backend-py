from src.util import logger, settings, helper
from src.services import aws
import json
import urllib.request, json

LOGGER = logger.RotatingLogger(__name__).getLogger()

class engine(object):
    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    def get_fundamental(self, ticker):
        try:
            awse = aws.engine()
            sravz_id = ticker['SravzId']
            code = ticker['APICode']
            helper.empty_cache_if_new_day()
            collection_name = f"{sravz_id}"
            prefix = f"{settings.constants.SRAVZ_DATA_MUTUAL_FUNDS_FUNDAMENTALS_PREFIX}{collection_name}.json"
            if not awse.is_file_uploaded_n_days_back(settings.constants.SRAVZ_DATA_S3_BUCKET, 
                                                     prefix, 
                                                     settings.constants.MUTUAL_FUNDS_FUNDAMENTAL_DATA_DAYS_BEFORE_UPDATE):
                url = "{0}/api/fundamentals/{1}?api_token={2}&order=d&fmt=json".format(settings.constants.EOD_URL, 
                                                                                       code, 
                                                                                       settings.constants.EODHISTORICALDATA_API_KEY)
                json_data = urllib.request.urlopen(url).read()
                data  = json.loads(json_data)
                awse.upload_quotes_to_contabo(data, collection_name, prefix = prefix)
                return (True, sravz_id)
        except Exception:
            LOGGER.error('Failed to process fundamental for ticker {0}'.format(sravz_id), exc_info=True)
        return (False, sravz_id)

    def get_fundamentals(self, tickers = []):
        '''
            tickers = [(code, sravz_id)]
            from src.services.stock.summary_stats import engine
            e = engine()
            e.get_fundamentals(tickers=[('stk_us_adbe', 'ADBE')])
        '''
        # tickers = (list(set(tickers)))
        return [self.get_fundamental(ticker) for ticker in tickers]

if __name__ == '__main__':
    pass



