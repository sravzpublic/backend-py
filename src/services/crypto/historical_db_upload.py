#!/usr/bin/env python
from datetime import timedelta
import datetime
from src.services.crypto.quotes import engine
from src.services.crypto.hash import engine as hash_engine
from src.util import settings, logger
from src.util.settings import constants


def upload(tickers=None):
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        e = engine()
        e.get_eodhistoricaldata_historical_crypto_quotes(
            tickers=tickers, upload_to_db=True, ndays_back=None)
    except Exception:
        _logger.error(
            'Could not upload historical crypto quotes', exc_info=True)

if __name__ == '__main__':
    upload()
