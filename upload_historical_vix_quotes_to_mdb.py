#!/usr/bin/env python
from datetime import timedelta
import datetime
from src.services.vix.quotes import engine
from src.util import settings, logger
from src.util.settings import constants


def upload(tickers=None):
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        e = engine()
        e.get_historical_vix_quotes(
            tickers=tickers, upload_to_db=True, ndays_back=constants.NDAY_BACK_FOR_HISTORICAL_QUOTES)
    except Exception:
        _logger.error(
            'Could not upload historical vix quotes', exc_info=True)


if __name__ == '__main__':
    upload()
