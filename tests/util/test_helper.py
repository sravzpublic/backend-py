from unittest.mock import patch
from src.util import helper, settings
import pytest
def test_ticker_type():
    assert helper.get_ticker_type('stk_') == settings.constants.TICKER_TYPE_STOCK
    assert helper.get_ticker_type('fut_') == settings.constants.TICKER_TYPE_FUTURE
    assert helper.get_ticker_type('fund_') == settings.constants.TICKER_TYPE_MUTUAL_FUND
    assert helper.get_ticker_type('etf_') == settings.constants.TICKER_TYPE_ETF

# Define test cases
@pytest.mark.parametrize("current_day, expected_result", [
    (1, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
    (15, [140, 141, 142, 143, 144, 145, 146, 147, 148, 149]),
    (30, [290, 291, 292, 293, 294, 295, 296, 297, 298, 299])
])

def test_get_part_based_on_day(current_day, expected_result):
    # Mocpatchetime.datetime.now().day
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value.day = current_day
        
        # Call the function with mocked current day
        result = helper.get_list_part_based_on_day(list(range(300)))
    
    # Check the result
    assert result == expected_result