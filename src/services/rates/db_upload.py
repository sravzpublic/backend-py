#!/usr/bin/env python
from datetime import timedelta
import datetime
from src.services.rates.quotes import engine
from src.util import settings, logger
from src.util.settings import constants

def upload(tickers = None):
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
       e = engine()
       e.get_rate_quotes(upload_to_db = True)
    except Exception:
       _logger.error('Could not upload rate quotes', exc_info=True)

    try:
       e = engine()
       e.get_mortgage_rates_quotes(upload_to_db = True)
    except Exception:
       _logger.error('Could not upload mortgage rate quotes', exc_info=True)

if __name__ == '__main__':
    upload()
