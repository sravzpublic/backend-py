from src.util import logger
from src.services.kafka_helpers.message_contracts import MessageContracts
import unittest

LOGGER = logger.RotatingLogger(__name__).getLogger()

def test_pca_scatter_plot():
    msg = {"id": 5, "p_i": {"args": [["fut_us_gc", "fut_us_nq"]], "kwargs": {"upload_to_aws": True, "device":"mobile"}}, "k_i": {"return_aws_info_only": True}, "t_o": "vagrant_portfolio1", "d_o": None, "cid": "26APtPOiIyFhsm5QAAAF", "fun_n": "get_covariance_matrix", "e": "Error"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None


def test_pca_engine_get_covariance_matrix():
    msg = {"id": 7, "p_i": {"args": [["fut_us_gc", "fut_us_nq"]], "kwargs": {"upload_to_aws": True, "device":"mobile"}}, "k_i": {"return_aws_info_only": True}, "t_o": "vagrant_portfolio1", "d_o": None, "cid": "26APtPOiIyFhsm5QAAAF", "fun_n": "get_covariance_matrix", "e": "Error"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None


def test_chart_engine_combined_chart():
    msg_in = {"id": 9, "p_i": {"args": [["fut_us_gc", "fut_us_nq"]], "kwargs": {"upload_to_aws": True}}, "k_i": {"return_aws_info_only": True}, "t_o": "portfolio1", "d_o": ""}
    x = MessageContracts.get_output_message(msg_in)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None

def test_risk_engine_returns_tear_sheet():
    msg = {"id":14,"p_i":{"args":["fut_gold"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None

def test_pca_components():
    msg = {'id': 6, 'p_i': {'args': [["etf_us_qqq", "etf_us_qld"]], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None

@unittest.skip("Skipping portfolio not supported")
def test_pca_components_vs_index_returns():
    msg = {'id': 6.1, 'p_i': {'args': [["fut_us_gc", "fut_us_nq"]], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None

@unittest.skip("Skipping portfolio not supported")
def test_pca_component_create_portfolio_pca_report():
    msg = {'id': 6.2, 'p_i': {'args': [['stk_us_AAPL', 'stk_us_AMZN', 'stk_us_FB', 'stk_us_GOOG', 'stk_us_NFLX']], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None

def test_get_rolling_stats():
    msg = {"id":10,"p_i":{"args":["fut_us_gc"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}    
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    

def test_get_dickey_fuller():
    msg = {"id":11,"p_i":{"args":["fut_platinum"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    

def test_get_dickey_fuller():
    msg = {"id":11,"p_i":{"args":["fut_platinum"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    

def test_get_rolling_stats_by_mean_10_days():
    msg = {"id":12,"p_i":{"args":["fut_platinum", "mean", "10D"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    

def test_get_rolling_stats_by_std_10_days():
    msg = {"id":12,"p_i":{"args":["fut_platinum", "std", "10D"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    

def test_get_df_stats_by_sravz_id():
    msg = {"id":13,"p_i":{"args":["fut_us_gc"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None   

def test_get_returns_tear_sheet_by_sravz_id():
    msg = {"id":14,"p_i":{"args":["fut_gold"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None   

@unittest.skip("Skipping portfolio not supported")
def test_get_returns_tear_sheet_by_portfolio():
    msg = {"id":15,"p_i":{"args":['Goldoilspx', '5af375146d157413f4945e1b'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None   
        
def test_get_timeseries_analysis():
    msg = {"id":16,"p_i":{"args":['stk_us_fb'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None   

@unittest.skip("Skipping portfolio not supported")           
def test_get_portfolio_returns_timeseries_analysis():
    msg = {"id":17,"p_i":{"args":['GoldAndOil1', '5af375146d157413f4945e1b'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None   

def test_get_get_bayesian_tear_sheet():
    msg = {"id":18,"p_i":{"args":['fut_us_gc'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None   

def test_get_get_bayesian_tear_sheet():
    msg = {"id":18,"p_i":{"args":['fut_us_gc'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None                                   

def test_prophet_model():
    for item in [19.1, 19.2, 19.3, 19.4, 19.5, 19.6]:
        msg = {"id":item,"p_i":{"args":['fut_us_gc'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
        x = MessageContracts.get_output_message(msg)
        assert x['d_o'] is not None
        assert x['e'] == ''
        assert x['d_o']['signed_url'] is not None     

@unittest.skip("Skipping portfolio not supported")
def test_prophet_model_portfolio():
    for item in [20.1, 20.2, 20.3, 20.4, 20.5, 20.6]:
        msg = {"id":item,"p_i":{"args":['GoldAndOil', '5af375146d157413f4945e1b'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
        x = MessageContracts.get_output_message(msg)
        assert x['d_o'] is not None
        assert x['e'] == ''
        assert x['d_o']['signed_url'] is not None    

@unittest.skip("Skipping portfolio not supported")
def test_get_portfolio_correlation_analysis_tear_sheet():
    msg = {"id":21,"p_i":{"args":['GoldAndOil', '5af375146d157413f4945e1b'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    

@unittest.skip("Skipping portfolio not supported")
def test_get_correlation_analysis_tear_sheet_user_asset():
    msg = {"id":22,"p_i":{"args":[''],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    

@unittest.skip("Skipping portfolio not supported")
def test_get_crypto_tear_sheet():
    msg = {"id":23,"p_i":{"args":['crypto_btc_usd'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    x = MessageContracts.get_output_message(msg)
    assert x['d_o'] is not None
    assert x['e'] == ''
    assert x['d_o']['signed_url'] is not None    
