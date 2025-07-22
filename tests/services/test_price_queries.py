from src.services import aws
from src.util import settings
from src.services.price_queries import engine
from src.services.cache import Cache
from unittest.mock import Mock
import pytest

def test_get_historical_price_contabo():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_CONTABO)
    pe = engine()
    Cache.Instance().remove_all()
    data = pe.get_historical_price('test', src=settings.constants.S3_TARGET_CONTABO)
    assert data == "hello world"

def test_get_historical_price_aws():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_AWS)
    pe = engine()
    Cache.Instance().remove_all()
    data = pe.get_historical_price('test', src=settings.constants.S3_TARGET_AWS)
    assert data == "hello world"


def test_get_historical_price_idrivee2():
    awse = aws.engine()
    awse.upload_quotes_to_contabo( "hello world", "test", target=settings.constants.S3_TARGET_IDRIVEE2)
    pe = engine()
    Cache.Instance().remove_all()
    data = pe.get_historical_price('test', src=settings.constants.S3_TARGET_IDRIVEE2)
    assert data == "hello world"

@pytest.fixture
def mock_awse(mocker):
    mock = Mock()
    mocker.patch('src.services.aws.engine', return_value=mock)
    return mock

def test_get_historical_mutual_fund_price(mock_awse):
    pe = engine()
    mock_awse.download_quotes_from_contabo.return_value = 'mocked value'
    Cache.Instance().remove_all()
    data = pe.get_historical_price('fund_test')
    assert data == "mocked value"
    mock_awse.download_quotes_from_contabo.assert_called_with('fund_test', target=settings.constants.S3_TARGET_CONTABO)

def test_get_historical_mutual_fund_price_from_second_source(mock_awse):
    pe = engine()
    def side_effect(*args, **kwargs):
        if kwargs['target'] == settings.constants.S3_TARGET_CONTABO:
            raise ValueError("No price data")
        if kwargs['target'] == settings.constants.S3_TARGET_IDRIVEE2:
            return 'mocked value'
    mock_awse.download_quotes_from_contabo.side_effect = side_effect
    Cache.Instance().remove_all()
    data = pe.get_historical_price('fund_test')
    assert data == "mocked value"
    mock_awse.download_quotes_from_contabo.assert_called_with('fund_test', target=settings.constants.S3_TARGET_IDRIVEE2)

def test_get_historical_mutual_fund_price_no_source_available(mock_awse):
    pe = engine()
    def side_effect(*args, **kwargs):
        if kwargs['target'] == settings.constants.S3_TARGET_CONTABO:
            raise ValueError("No price data")
        if kwargs['target'] == settings.constants.S3_TARGET_IDRIVEE2:
            raise ValueError("No price data")
    mock_awse.download_quotes_from_contabo.side_effect = side_effect
    Cache.Instance().remove_all()
    data = pe.get_historical_price('fund_test')
    assert data is None
    
def test_get_historical_etf_fund_price(mock_awse):
    pe = engine()
    mock_awse.download_quotes_from_contabo.return_value = 'mocked value'
    Cache.Instance().remove_all()
    data = pe.get_historical_price('etf_test')
    assert data == "mocked value"
    mock_awse.download_quotes_from_contabo.assert_called_with('etf_test', target=settings.constants.S3_TARGET_CONTABO)

def test_get_historical_etf_price_from_second_source(mock_awse):
    pe = engine()
    def side_effect(*args, **kwargs):
        if kwargs['target'] == settings.constants.S3_TARGET_CONTABO:
            raise ValueError("No price data")
        if kwargs['target'] == settings.constants.S3_TARGET_IDRIVEE2:
            return 'mocked value'
    mock_awse.download_quotes_from_contabo.side_effect = side_effect
    Cache.Instance().remove_all()
    data = pe.get_historical_price('etf_test')
    assert data == "mocked value"
    mock_awse.download_quotes_from_contabo.assert_called_with('etf_test', target=settings.constants.S3_TARGET_IDRIVEE2)

def test_get_historical_etf_fund_price_no_source_available(mock_awse):
    pe = engine()
    def side_effect(*args, **kwargs):
        if kwargs['target'] == settings.constants.S3_TARGET_CONTABO:
            raise ValueError("No price data")
        if kwargs['target'] == settings.constants.S3_TARGET_IDRIVEE2:
            raise ValueError("No price data")
    mock_awse.download_quotes_from_contabo.side_effect = side_effect
    Cache.Instance().remove_all()
    data = pe.get_historical_price('etf_test')
    assert data is None

def test_get_historical_price_cache_not_updated_when_no_data(mock_awse):
    pe = engine()
    def side_effect(*args, **kwargs):
        if kwargs['target'] == settings.constants.S3_TARGET_CONTABO:
            raise ValueError("No price data")
        if kwargs['target'] == settings.constants.S3_TARGET_IDRIVEE2:
            raise ValueError("No price data")
    mock_awse.download_quotes_from_contabo.side_effect = side_effect
    Cache.Instance().remove_all()
    data = pe.get_historical_price('fund_test')
    assert data is None
    cache_key = 'get_historical_price_%s'%('fund_test')
    value = Cache.Instance().get(cache_key)
    assert value is None

def test_get_historical_price_calls_aws_s3_by_default(mock_awse):
    pe = engine()
    Cache.Instance().remove_all()
    mock_awse.download_quotes_from_contabo.return_value = 'mocked value'
    data = pe.get_historical_price('stk_test')
    assert data == "mocked value"
    mock_awse.download_quotes_from_contabo.assert_called_with('stk_test', target='contabo')
