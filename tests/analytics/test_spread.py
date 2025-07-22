import pytest
from src.util import logger, settings
from src.services.stock import historical_quotes
from unittest.mock import Mock
from src.services import aws
from src.analytics import spread

def test_create_returns_tear_sheet():
    spread.perform_spread_analysis()
    awse = aws.engine()
    status = awse.is_file_uploaded_today(settings.constants.CONTABO_BUCKET, 
                                         f'{settings.constants.CONTABO_BUCKET_PREFIX}/assets/10yr-vs-5yr-us-treasury-analysis.jpg',
                                         provider=settings.constants.S3_TARGET_CONTABO)
    assert status is True