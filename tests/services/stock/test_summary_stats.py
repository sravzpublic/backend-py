import pytest
from src.services.stock import summary_stats
from unittest.mock import Mock, ANY
from src.services import price_queries
from unittest.mock import patch
from src.analytics import pca
from src.services import aws
import pandas as  pd
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.services.stock.summary_stats import upload_quotes_stats_df_to_s3

pqe = price_queries.engine()
pcae = pca.engine()
summary_stats_engine = summary_stats.engine()
awse = aws.engine()

@pytest.fixture
def mock_awse(mocker):
    mock = Mock()
    mocker.patch('src.services.aws.engine', return_value=mock)
    return mock

def test_upload_pyfolio_stats_df(mock_awse):
    summary_stats.upload_pyfolio_stats_df('stk_us_abbv', pcae, mock_awse)
    mock_awse.upload_quotes_to_contabo.assert_called
    mock_awse.upload_quotes_to_contabo.assert_called_with(ANY, "stk_us_abbv_stats")

def test_upload_summary_stats_df(mock_awse):
    summary_stats.upload_summary_stats_df('stk_us_abbv', pqe, mock_awse)
    # summary_stats.upload_summary_stats_df('stk_us_abbv', pqe, awse)
    mock_awse.upload_quotes_to_contabo.assert_called
    mock_awse.upload_quotes_to_contabo.assert_called_with(ANY, "stk_us_abbv_summary_stats")    

def test_summary_stats_enging_quotes_parquet_file_uploads():
    with patch("awswrangler.s3.to_parquet") as mock_to_parquet:
        summary_stats_engine.upload_final_stats_df(['stk_us_abbv'])
        # Extract actual call arguments
        called_args, called_kwargs = mock_to_parquet.call_args
        assert len(called_args[0]) == 1
        assert called_args[1] in ["s3://sravz-data/historical/quotes_stats.parquet", 
                                  "s3://sravz-data/historical/quotes_summary_stats.parquet"]

def test_integration_upload_quotes_stats_df():
    e = summary_stats.engine()    
    # Change the target s3 so the prod files are not overwritten
    e.STATS_TARGET_S3 = "quotes_stats_test"
    e.SUMMARY_STATS_TARGET_S3 = "quotes_summary_stats_test"    
    # Calculate stats for only two tickers to speed up the test
    e.get_summary_stats(tickers=['stk_us_zoom', 'stk_us_mmm'])
    e.upload_final_stats_df(tickers=['stk_us_zoom', 'stk_us_mmm'])    

    df_aws_quotes_stats = e.get_quotes_stats_df(s3_file_name="quotes_stats_test", src='aws')
    df_aws_summary_stats = e.get_quotes_stats_df(s3_file_name="quotes_summary_stats_test", src='aws')
    assert not df_aws_quotes_stats.empty
    assert not df_aws_summary_stats.empty
    assert 'sravz_id' in df_aws_quotes_stats.columns
    assert 'sravz_id' in df_aws_summary_stats.columns

    df_contabo_quotes_stats = e.get_quotes_stats_df(s3_file_name="quotes_stats_test", src='contabo')
    df_contabo_summary_stats = e.get_quotes_stats_df(s3_file_name="quotes_summary_stats_test", src='contabo')
    assert not df_contabo_quotes_stats.empty
    assert not df_contabo_summary_stats.empty
    assert 'sravz_id' in df_contabo_quotes_stats.columns
    assert 'sravz_id' in df_contabo_summary_stats.columns
    
