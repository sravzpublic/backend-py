import pytest
from src.util import logger
from src.services.stock import historical_quotes
from unittest.mock import Mock

LOGGER = logger.RotatingLogger(__name__).getLogger()

@pytest.fixture
def mock_awse(mocker):
    mock = Mock()
    mocker.patch('src.services.aws.engine', return_value=mock)
    return mock

def test_upload_ticker(mock_awse):
    ticker, status = historical_quotes.upload_ticker('aapl')
    mock_awse.upload_quotes_to_contabo.assert_called
    