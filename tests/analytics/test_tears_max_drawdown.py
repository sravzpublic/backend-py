from src.util import settings
from src.services import aws
from src.analytics import tears_max_drawdown

def test_create_returns_tear_sheet():
    sravzid = 'fut_us_gc'
    tears_max_drawdown.create_returns_tear_sheet(sravzid)   
    awse = aws.engine()
    status = awse.is_file_uploaded_today(settings.constants.CONTABO_BUCKET, 
                                         f'{settings.constants.CONTABO_BUCKET_PREFIX}/assets/{sravzid}_worst_drawdown_statistics.jpg', 
                                         provider=settings.constants.S3_TARGET_CONTABO)
    assert status is True