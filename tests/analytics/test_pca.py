from src.analytics import pca
import unittest
from unittest.mock import Mock, patch, ANY
from src.util import aws_cache, settings
from pathlib import Path

class TestGetCollectionItems(unittest.TestCase):
    def setUp(self):
        # Initialize YourClass instance
        self.engine = pca.engine()

    @patch.object(pca.engine, "handle_cache_aws")
    def test_create_returns_tear_sheet(self, mock_handle_cache_aws):
        e = pca.engine()
        _ = e.get_scatter_plot_data(['stk_us_cvna', 'stk_us_twlo'], 10)
        mock_handle_cache_aws.assert_called_once_with('get_scatter_plot_data_6eb6f59e22619179f1fac129888e2314_pca_10', 
                                                      'sravz-scatter-plot-pca', 
                                                      'get_scatter_plot_data_pca_by_timeframe_6eb6f59e22619179f1fac129888e2314_10', 
                                                      ANY, 
                                                      False)
        dfs_list = mock_handle_cache_aws.call_args.args[3]()
        assert len(dfs_list), "DataFrame should not be empty"
        assert all(not df.empty for df in dfs_list), "Some DataFrames are empty"

    def test_get_price_data_dfs(self):
        df = self.engine.get_price_data_dfs(['stk_us_cvna', 'stk_us_twlo'])
        assert not df.empty, "DataFrame should not be empty"

    def test_get_percent_daily_returns(self):
        df = self.engine.get_percent_daily_returns(['stk_us_cvna', 'stk_us_twlo'])
        assert not df.empty, "DataFrame should not be empty"
        assert df.index.is_monotonic_increasing, "Index is not in increasing order"
        assert df.fillna(method="ffill").equals(df), "DataFrame has unfilled NaN values"

    @patch.object(aws_cache.engine, "handle_cache_aws")
    def test_get_scatter_plot_daily_return_dataframe_for_pc(self, mock_handle_cache_aws):
        _ = self.engine.get_scatter_plot_daily_return(['stk_us_cvna', 'stk_us_twlo'])
        mock_handle_cache_aws.assert_called_once_with('get_scatter_plot_daily_return_6eb6f59e22619179f1fac129888e2314_pca_10', 'sravz-scatter-plot-pca', 'get_scatter_plot_daily_return_pca_by_timeframe_6eb6f59e22619179f1fac129888e2314_10', ANY, False)
        df = mock_handle_cache_aws.call_args.args[3]()
        assert not df.empty, "DataFrame should not be empty"

    @patch.object(aws_cache.engine, "handle_cache_aws")
    def test_get_scatter_plot_daily_return_dataframe_for_pc(self, mock_handle_cache_aws):
        _ = self.engine.get_scatter_plot_daily_return(['stk_us_cvna', 'stk_us_twlo'], device=settings.constants.DEVICE_TYPE_MOBILE)
        mock_handle_cache_aws.assert_called_once_with('get_scatter_plot_daily_return_6eb6f59e22619179f1fac129888e2314_pca_10', 'sravz-scatter-plot-pca', 'get_scatter_plot_daily_return_pca_by_timeframe_6eb6f59e22619179f1fac129888e2314_10', ANY, False)
        data_files = mock_handle_cache_aws.call_args.args[3]()
        assert data_files['scatter_plot'] , "Scatter plot file is not present"
        file_path = Path(data_files['scatter_plot'] )
        assert file_path.exists(), f"File not found: {file_path}"


    @patch.object(aws_cache.engine, "handle_cache_aws")
    def test_get_get_pca_components(self, mock_handle_cache_aws):
        _ = self.engine.get_pca_components(['stk_us_cvna', 'stk_us_twlo'])
        mock_handle_cache_aws.assert_called_once_with('get_pca_components_6eb6f59e22619179f1fac129888e2314_pca_2', 
                                                      'sravz-components-pca', 
                                                      'get_pca_components_pca_6eb6f59e22619179f1fac129888e2314_2',
                                                        ANY,
                                                        False)
        # Cannot call due to recursive calls to aws cache
        # data_files = mock_handle_cache_aws.call_args.args[3]()
        # assert data_files['explained_variance_fig'] , "Explained variable figure not generated"
        # file_path = Path(data_files['explained_variance_fig'] )
        # assert file_path.exists(), f"File not found: {file_path}"