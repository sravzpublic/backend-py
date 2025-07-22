from src.services import aws
from src.services.etfs import mutual_funds_historical_quotes
from src.util import settings

def test_upload_ticker_idrivee2():
    awse = aws.engine()
    mutual_funds_historical_quotes.upload_ticker({'_id': None, 'APICode':'AAAEX.US', 'SravzId': 'fund_us_aaaex'})
    status = awse.is_quote_updated_today('fund_us_aaaex', provider=settings.constants.S3_TARGET_IDRIVEE2)
    assert status is True      

def test_upload_ticker_contabo():
    awse = aws.engine()
    mutual_funds_historical_quotes.upload_ticker({'_id': None, 'APICode':'AAAEX.US', 'SravzId': 'fund_us_aaaex'})
    contabo_status = awse.is_quote_updated_today('fund_us_aaaex', provider=settings.constants.S3_TARGET_CONTABO)
    assert contabo_status is True       
    