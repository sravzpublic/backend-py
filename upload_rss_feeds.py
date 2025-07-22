#!/usr/bin/env python
from src.services.rss import parser
from src.util import logger

if __name__ == '__main__':
    _logger = logger.RotatingLogger(__name__).getLogger()
    pe = parser.engine()
    try:
        pe.upload_feeds()
    except Exception:
        _logger.error('Could not upload rss feeds', exc_info=True)
    _logger.info('Uploaded RSS Feeds')
