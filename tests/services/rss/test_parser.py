from src.util import logger
from src.services.rss import parser
from src.util import logger
LOGGER = logger.RotatingLogger(__name__).getLogger()

def test_upload_rss_feeds():
    _logger = logger.RotatingLogger(__name__).getLogger()
    pe = parser.engine()
    try:
        pe.upload_feeds()
    except Exception:
        _logger.error('Could not upload rss feeds', exc_info=True)
    _logger.info('Uploaded RSS Feeds')
    