#!/usr/bin/env python
import json
import datetime
from src.services.assets import indices
from src.util import settings, logger
from src.analytics import charts


def upload():
    _logger = logger.RotatingLogger(__name__).getLogger()
    try:
        indices.upload_index_components_to_s3()
        _logger.info('Uploaded index components to S3')
    except Exception:
        _logger.error('Could not upload index components to S3', exc_info=True)

    try:
        indices.upload_index_components_to_mdb()
        _logger.info('Uploaded index components to mdb')
    except Exception:
        _logger.error('Could not upload index components to mdb', exc_info=True)

    try:
        chartse = charts.engine()
        chartse.get_eod_all_index_components_bar_charts()
        _logger.info('Components Bar Charts Created')
    except Exception:
        _logger.error('Could not upload Index components charts', exc_info=True)


if __name__ == '__main__':
    upload()
