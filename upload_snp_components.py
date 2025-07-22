#!/usr/bin/env python
import json
import datetime
from src.services.snp import components
from src.util import settings, logger


def upload():
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        snp_components_engine = components.engine()
        snp_components_engine.get_snp_components(upload_to_db = True)
    except Exception:
        _logger.error('Could not upload SNP components to DB', exc_info=True)

    _logger.info('SNP Components Uploaded')


if __name__ == '__main__':
    upload()

