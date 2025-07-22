from unittest.mock import Mock, patch
import pytest
from src.services.mutual_funds import fundamentals
from src.util import settings

# Required: pip install pytest-mock
@pytest.fixture
def mock_awse(mocker):
    mock = Mock()
    mocker.patch('src.services.aws.engine', return_value=mock)
    return mock

def test_get_fundamentals():
    fundamentals_engine = fundamentals.engine()
    def side_effect(*args, **kwargs):
        return (True, "Ticker")
    fundamentals_engine.get_fundamental = side_effect
    value = fundamentals_engine.get_fundamentals([('stk_us_adbe', 'ADBE')])    
    assert value == [(True, 'Ticker')]

def test_get_fundamental(mock_awse):
    fundamentals_engine = fundamentals.engine()
    mock_awse.is_file_uploaded_n_days_back.return_value = False  # Simulate file not uploaded
    mock_awse.upload_quotes_to_contabo.return_value = None  # Simulate successful upload

    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.return_value.read.return_value = b'[{"data": "example"}]'  # Simulate response data
        # Call the method
        result = fundamentals_engine.get_fundamental({'SravzId': 'sravz_id', 
                                                      'APICode': 'code'})
        # Assertions
        assert result == (True, 'sravz_id')
        fundamentals_engine.awse.is_file_uploaded_n_days_back.assert_called_once_with(
            settings.constants.SRAVZ_DATA_S3_BUCKET,
            f"{settings.constants.SRAVZ_DATA_MUTUAL_FUNDS_FUNDAMENTALS_PREFIX}sravz_id.json", 
            30)
        mock_urlopen.assert_called_once_with(
            f'https://eodhistoricaldata.com/api/fundamentals/code?api_token={settings.constants.EODHISTORICALDATA_API_KEY}&order=d&fmt=json')
        fundamentals_engine.awse.upload_quotes_to_contabo.assert_called_once_with([{'data': 'example'}], 
                                                                                  'sravz_id',
                                                                                  prefix=f"{settings.constants.SRAVZ_DATA_MUTUAL_FUNDS_FUNDAMENTALS_PREFIX}sravz_id.json")

    