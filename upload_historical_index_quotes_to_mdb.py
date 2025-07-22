#!/usr/bin/env python
from datetime import timedelta
import datetime
from src.services.etfs.index_historical_quotes import engine
from src.util import settings, logger
from src.util.settings import constants


def upload_historical_quotes(tickers=None):
    '''
        To upload specific index:
        upload_historical_quotes(tickers=[{'Code': 'GSPC', 'SravzId': 'idx_us_gspc', '_id': None}])
    '''
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        e = engine()
        e.get_eodhistoricaldata_historical_index_quotes(
            tickers=tickers, upload_to_db=True, ndays_back=constants.NDAY_BACK_FOR_HISTORICAL_QUOTES)
    except Exception:
        _logger.error(
            'Could not upload historical US index quotes', exc_info=True)


if __name__ == '__main__':
    upload_historical_quotes()
