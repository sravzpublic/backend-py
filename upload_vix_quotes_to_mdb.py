#!/usr/bin/env python
import datetime
from src.services.vix.quotes import engine
from src.util import logger
from src.util.settings import constants

def upload():
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        e = engine()
        datetime.datetime.now().strftime("%Y-%m-%d")
        e.get_vix_quotes(None, upload_to_db = True)
    except Exception:
        _logger.error('Could not upload vix quotes', exc_info=True)

if __name__ == '__main__':
    upload()

