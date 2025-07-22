#!/usr/bin/env python
import json
import datetime
from src.services.assets import exchanges
from src.util import settings, logger


def upload():
    _logger = logger.RotatingLogger(__name__).getLogger()
    try:
        exchanges.upload_exchange_components_to_s3()
        _logger.info('Uploaded exchange components to S3')
    except Exception:
        _logger.error('Could not upload exchange components to S3', exc_info=True)

    try:
        exchanges.upload_exchange_components_to_mdb()
        _logger.info('Uploaded exchange components to mdb')
    except Exception:
        _logger.error('Could not upload exchange components to mdb', exc_info=True)

if __name__ == '__main__':
    upload()
