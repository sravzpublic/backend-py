#!/usr/bin/env python
import datetime
from src.services.etfs.quotes import engine
from src.util import logger


def upload(tickers = []):
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        e = engine()
        datetime.datetime.now().strftime("%Y-%m-%d")
        e.get_eodhistoricaldata_index_quotes(tickers = tickers, upload_to_db = True)
    except Exception:
        _logger.error('Could not upload Index quotes', exc_info=True)

if __name__ == '__main__':
    tickers = None # [{'_id': None, 'Code': 'GSPC', 'Country': 'US'}]
    upload(tickers=tickers)

