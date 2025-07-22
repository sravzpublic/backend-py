#!/usr/bin/env python
from src.services.currency.quotes import engine
from src.util import logger
from src.util.settings import constants


def upload(tickers=None):
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        e = engine()
        e.get_eodhistoricaldata_historical_currency_quotes(
            tickers=tickers, upload_to_db=True, ndays_back=constants.NDAY_BACK_FOR_HISTORICAL_QUOTES)
    except Exception:
        _logger.error(
            'Could not upload historical currency quotes', exc_info=True)


if __name__ == '__main__':
    upload()
