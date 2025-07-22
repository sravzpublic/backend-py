#!/usr/bin/env python
import datetime
from src.services.crypto.quotes import engine
from src.util import logger
from src.util.settings import constants

def upload():
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        e = engine()
        datetime.datetime.now().strftime("%Y-%m-%d")
        e.get_eodhistoricaldata_crypto_quotes(upload_to_db = True)
    except Exception:
        _logger.error('Could not upload crypto quotes', exc_info=True)

if __name__ == '__main__':
    upload()

