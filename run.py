import os
import matplotlib
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import json
from src.services import ecocal
import uuid
import pyfolio as pf
from src.services.etfs import index_historical_quotes
from src.services.crypto.quotes import engine as crytp_quotes_engine
from src.services.crypto.hash import engine as crytp_hash_engine
from src.services.rates.quotes import engine as rates_quotes_engine
from src.services.vix.quotes import engine as vix_quotes_engine
from src.services.currency.quotes import engine as currency_quotes_engine
from src.services.etfs.quotes import engine as index_quotes_engine
from src.services.stock.quotes import engine as stock_quotes_engine
from src.services.price import engine as commodities_quotes_engine
from src.services.quotes_providers import marketwatch, yahoo, eodhistoricaldata
from src.analytics import pca, risk, portfolio, stocker
from src.util.helper import is_user_asset
from src.util import helper
from src.services.treasury import engine as treasury_engine
from src.services import price, mdb
from src.services.assets import sravz_assets
from src.services.assets import indices as sravz_assets_indices
from src.services.assets import crypto as sravz_assets_crypto
from src.services.assets import forex as sravz_assets_forex
from src.services.assets import exchanges as sravz_assets_exchanges
from src.services.etfs import russell, index_components, russell_2000
from src.services.quotes_providers.quote import engine as quote_engine
from src.services.stock import historical_quotes
from src.services.stock.quotes import engine
from src.analytics import pnl
from src.services.etfs import dj30, all_ordinaires, bse_sensex_components, \
ftse_bursa_malaysia, ftse_uk_100, dax, cac40, obx, ta125
from src.services.stock import components
from src.services import ecocal, quotes_providers
from src.util import plot
from src.services.quotes_providers import moneycontrol
from src.services import price_queries, webcrawler
from src.analytics import stats, timeseries, tears, stocker_tears, charts
from src.util import settings
from src.services import aws
from src.services.kafka_helpers.message_contracts import MessageContracts
from src.analytics import pca, util
from src.services.dashboard import upload_from_db_to_s3 as dasboard_upload_from_db_to_s3
from src.services.bond import historical_quotes as bond_historical_quotes
# Quote engines


if __name__ == '__main__':
    # pcae = pca.engine()

    e = charts.engine()
    x = e.get_combined_chart(['stk_us_cvna', 'stk_us_twlo'], upload_to_aws = True)
    #x = e.get_combined_chart(['fut_oil_feb_17_usd_lme', 'fut_gold_feb_17_usd_lme'], upload_to_aws = True, device = settings.constants.DEVICE_TYPE_MOBILE)
    #x = e.get_combined_chart(['stk_testuser_test_asset.csv_1549155135802'], upload_to_aws = False, device = settings.constants.DEVICE_TYPE_PC)
    #x = e.get_combined_chart(['fut_gold', 'stk_testuser_test_asset.csv_1549155135802'], upload_to_aws = False, device = settings.constants.DEVICE_TYPE_MOBILE)
    #x = e.get_combined_chart(['fut_gold', 'stk_us_abbv'], upload_to_aws = False, device = settings.constants.DEVICE_TYPE_MOBILE)
    #x = e.get_combined_chart(['fut_gold', 'stk_testuser_test_asset.csv_1549155135802'], upload_to_aws = False, device = settings.constants.DEVICE_TYPE_PC)
    print(x)
    # Perform enconding and create the response message
    #msg_in = '{"id": 9, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}'
    #msg_in = '{"id": 9, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": false}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}'
    #msg_in =  '{"id": 7, "p_i": {"args":[["fut_gold_jun_18_usd_lme","fut_oil_jul_18_usd_lme"]],"kwargs":{"upload_to_aws":true },"k_i":{"return_aws_info_only":true},"t_o":"vagrant_portfolio1","d_o":null,"cid":"l3YMg0Szm05EFrZIAAAA"}'
    #msg_in =  '{"id":7, "p_i":{   "args":[[ "fut_gold_jun_18_usd_lme", "fut_oil_jul_18_usd_lme" ]], "kwargs":{"upload_to_aws":true }}, "k_i": { "return_aws_info_only":true }, "t_o":"vagrant_portfolio1", "d_o":null, "cid":"l3YMg0Szm05EFrZIAAAA" }'
    #msg = {"id": 7, "p_i": {"args": [["fut_gold_jun_18_usd_lme", "fut_oil_jul_18_usd_lme"]], "kwargs": {"upload_to_aws": True, "device":"mobile"}}, "k_i": {"return_aws_info_only": True}, "t_o": "vagrant_portfolio1", "d_o": None, "cid": "26APtPOiIyFhsm5QAAAF", "fun_n": "get_covariance_matrix", "e": "Error"}
    # Scatter plot
    #msg = {'id': 5, 'p_i': {'args': [['fut_gold_jun_18_usd_lme', 'fut_oil_jul_18_usd_lme']], 'kwargs': {'upload_to_aws': True, "device":"mobile"}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    #msg = {'id': 5, 'p_i': {'args': [["idx_us_gspc", "idx_us_COMP", "idx_us_DJIA"]], 'kwargs': {'upload_to_aws': False, "device":"mobile"}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    # PCA Components
    #msg = {'id': 6, 'p_i': {'args': [['fut_gold_jun_18_usd_lme', 'fut_oil_jul_18_usd_lme']], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    #msg = {'id': 6, 'p_i': {'args': [['fut_gold', 'fut_milk']], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    #msg = {'id': 6.1, 'p_i': {'args': [['fut_gold_jun_18_usd_lme', 'fut_oil_jul_18_usd_lme']], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    #msg = {'id': 6.2, 'p_i': {'args': [['stk_us_AAPL', 'stk_us_AMZN', 'stk_us_FB', 'stk_us_GOOG', 'stk_us_NFLX']], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    # 6.2: PCA_ENGINE.create_portfolio_pca_report,
    # msg = {'id': 6.2, 'p_i': {'args': ['test123123', '5f232d744f925716f94b5eee'], 'kwargs': {'upload_to_aws': True}}, 'k_i': {'return_aws_info_only': True}, 't_o': 'vagrant_portfolio1', 'd_o': None, 'cid': 'tSduZRIprFlMU9KnAAAR', 'fun_n': 'get_scatter_plot_daily_return'}
    # Get combined chart
    #msg = {"id": 9, "p_i": {"args": ["fut_gold_jun_18_usd_lme"], "kwargs": {"upload_to_aws": True}}, "k_i": {"return_aws_info_only": True}, "t_o": "vagrant_portfolio1", "d_o": None, "cid": "tSduZRIprFlMU9KnAAAR", "fun_n": "get_scatter_plot_daily_return"}
    #msg = {"id":9,"p_i":{"args":[["fut_gold","fut_silver","fut_platinum","fut_palladium", "stk_us_aapl", "stk_us_googl"]],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #msg = {"id":9.1,"p_i":{"args":[["fut_gold","fut_silver","fut_platinum","fut_palladium", "stk_us_aapl", "stk_us_googl"]],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #msg = {"id":9.1,"p_i":{"args":[["fut_gold","fut_silver","fut_platinum","fut_palladium", "stk_us_aapl", "stk_us_googl"]],"kwargs":{"upload_to_aws": False, "device":"pc"}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Get rolling stats
    #msg = {"id":10,"p_i":{"args":["fut_gold"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Get DF test
    #msg = {"id":11,"p_i":{"args":["fut_platinum"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Get rolling stats by timeframe
    #msg = {"id":12,"p_i":{"args":["fut_gold", "mean", 7],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #x = MessageContracts.get_output_message(msg)
    #msg = {"id":12,"p_i":{"args":["fut_gold", "mean", 7],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #x = MessageContracts.get_output_message(msg)
    #msg = {"id":12,"p_i":{"args":["fut_gold", "mean", 7],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #x = MessageContracts.get_output_message(msg)
    #msg = {"id":12,"p_i":{"args":["fut_gold", "mean", 7],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #x = MessageContracts.get_output_message(msg)
    #msg = {"id":12,"p_i":{"args":["fut_gold", "mean", 7],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #x = MessageContracts.get_output_message(msg)
    #msg = {"id":12,"p_i":{"args":["fut_gold", "std", 255],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Dickey Fuller Test. Old one do not use
    #msg = {"id": 1, "p_i": {"args": ["fut_gold_feb_17_usd_lme"], "kwargs": {"upload_to_aws": True}}, "k_i": {"return_aws_info_only": True}, "t_o": "", "d_o": None}
    #msg = {"id": 1.1, "p_i": {"args": ["fut_sugar"], "kwargs": {"upload_to_aws": True}}, "k_i": {"return_aws_info_only": True}, "t_o": "", "d_o": None}
    # Combined chart mobile
    #msg = {"id":9,"p_i":{"args":[["fut_gold", "fut_silver"]],"kwargs":{"upload_to_aws":True,"device":"mobile"}},"k_i":{"return_aws_info_only":True},"t_o":"vagrant_portfolio1","d_o":None,"cid":"ux5HYmZsArBWPij0AAAK","stopic":"combinedchart"}
    # User asset
    #msg = {"id":9,"p_i":{"args":[["stk_testuser_test_asset.csv_1549155135802"]],"kwargs":{"upload_to_aws":True,"device":"pc"}},"k_i":{"return_aws_info_only":True},"t_o":"vagrant_portfolio1","d_o":None,"cid":"sdr_alKoLlNkR37PAAAI","stopic":"combinedchart"}
    #x = MessageContracts.get_output_message(msg)
    # msg = {"id":13,"p_i":{"args":["fut_gold"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #msg = {"id":13,"p_i":{"args":["stk_testuser_daily_msft.1.csv_1550100549498"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Tearsheet asset:
    #msg = {"id":14,"p_i":{"args":["fut_gold"],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Tear sheet: portfolio
    #msg = {"id":15,"p_i":{"args":['Goldoilspx', '5af375146d157413f4945e1b'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #msg = {"id":16,"p_i":{"args":['stk_us_fb'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #msg = {"id":17,"p_i":{"args":['GoldAndOil1', '5af375146d157413f4945e1b'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #msg = {"id":18,"p_i":{"args":['fut_gold'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # prophet
    # for item in [19.1]:#, 19.2, 19.3, 19.4, 19.5, 19.6]:
    #     msg = {"id":item,"p_i":{"args":['fut_gold'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #     x = MessageContracts.get_output_message(msg)
    #     print(x)
    # msg = {"id":0,"p_i":{"args":['Hello'],"kwargs":{}},"k_i":{"return_aws_info_only": False},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    #msg = {"id":21,"p_i":{"args":['GoldAndOil', '5af375146d157413f4945e1b'],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # msg = {"id":22,"p_i":{"args":[''],"kwargs":{"upload_to_aws": True}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # msg = {"id":23,"p_i":{"args":[],"kwargs":{}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Live crypto quotes
    # msg = {"id":35,"p_i":{"args":[],"kwargs":{}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # live currency quotes
    # msg = {"id":34,"p_i":{"args":[],"kwargs":{}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Upload crypto histroical data
    # msg = {"id":41,"p_i":{"args":[],"kwargs":{}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Internal message
    # cron report
    # msg = {"id":44,"p_i":{"args":[],"kwargs":{}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # PNL report
    # msg = {"id":28,"p_i":{"args":[],"kwargs":{}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # Portfolio analysis
    # msg = {"id":20.6,"p_i":{"args":["TestPortfolio", "613ccfd365116d4c5bf6e5ba"],"kwargs":{}},"k_i":{"return_aws_info_only": True},"t_o":"vagrant_portfolio1","d_o": None,"cid":"I1GEA3vWK1OiAP6BAABk","stopic":"combinedchart"}
    # x = MessageContracts.get_output_message(msg)
    # # # x = MessageContracts.get_messages_in_progress()
    #print(x)

    #ae = aws.engine()
    # ae.check_bucket_exists('sravz-scatter-plot-pca')
    # Set cors rules
    # ae = aws.engine()
    #[ae.set_cors(item) for item in settings.constants.AWS_BUCKETS]
    # print(x)
    # ae.upload_if_file_not_found('sravz-charts', 'test', '/tmp/charts_get_combined_chart_fut_oil_fut_gold_mobile_settle.png')
    # print(ae.get_uploaded_objects_list('sravz-user-assets'))
    # print(ae.get_bucket_keys('sravz-user-assets'))
    # stats_engine = stats.engine()
    #stats_data = stats_engine.get_rolling_stats_by_sravz_id('fut_gold')
    # stats_data = stats_engine.get_rolling_stats_by_sravz_id('fut_gold')
    #print(stats_engine.get_df_stats_by_sravz_id('fut_gold', upload_to_aws = False))
    # ae.apply_life_cycle_policy('sravz-covariance-matrix-pca')
    # ae.apply_life_cycle_policy_to_all_buckets()
    # ae.apply_30_days_life_cycle_policy()
    # stats_engine.get_rollingstats_tear_sheet('fut_gold')
    # stats_engine.check_rolling_stats_alert_triggered('fut_us_gc')

    #pe = price_queries.engine()
    #print(pe.get_historical_price_df('fut_us_gc'))
    # print(pe.get_historical_price_df('idx_in_1'))
    #print(pe.get_historical_price('stk_us_eb'))
    #print(pe.get_historical_price_df('treasury_real_longterm_rate'))
    # print(pe.get_historical_price('testuser-daily_MSFT.1.csv-1548798147047'))
    # print(pe.get_historical_price_df('stk_testuser_test_asset.csv_1549155135802'))
    #plot.util.save_df_plot(plot.util.plot_df(data.cumsum()), 'fut_gold')

    #ecocal_engine = ecocal.engine()
    #ecocal_engine.get_eco_cal_from_web_by_date(upload_to_db = True)
    #ecocal_engine.get_day_eco_cal_from_web_for_day_range(upload_to_db = True, from_date = datetime.date(2018, 7, 1), end_date = datetime.date(2018, 7, 31))
    # ecocal_engine.get_all_weeks_eco_cal_from_web()

    #snp_components_engine = components.engine()
    #snp_components_engine.get_snp_components(upload_to_db = True)

    #stock_engine = stock_quotes_engine()
    # datetime.datetime.now().strftime("%Y-%m-%d")
    #stock_engine.get_quotes(upload_to_db = True)
    #print(stock_engine.get_quotes_from_eodhistoricaldata(tickers = ['AAPL']))

    #pnl_engine = pnl.engine()
    #pnl_engine.update()

    #stock_engine.get_quotes_from_cnnmoney(upload_to_db = False, tickers = ['UAA'])
    #stock_engine.get_quotes_from_nasdaq(upload_to_db = True, tickers = ['AMG'])
    #stock_engine.get_quotes_from_marketwatch(upload_to_db = True, tickers = ['GOOG'])
    #print(stock_engine.get_quotes_from_cnbc(tickers = ['AAPL','GOOG','IBM','C','SPX','UNH','FB', 'NFXL', 'AMZN']))
    #rint(stock_engine.get_quotes_from_fidelity(tickers = ['AAPL','GOOG','IBM','C','SPX','UNH','FB', 'NFLX', 'AMZN']))
    #stock_engine.get_xao_components_quotes()

    #stock_historical_quotes_engine = historical_quotes.engine()
    #stock_historical_quotes_engine.get_historical_snp_quotes(upload_to_db = True)
    # stock_historical_quotes_engine.get_historical_us_index_components_quotes(upload_to_db = True ,
    #tickers= ['ZM']
    #stock_historical_quotes_engine.get_eodhistoricaldata_historical_stock_quotes(tickers = tickers)

    # Uploads historical data
    # _quote_engine = quote_engine()
    # tickers = ['GOOG', 'AAPL', 'AMD']
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_STOOQ)
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_INVESTOPEDIA)
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_MACROTRENDS)
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_WSJ)
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_TIINGO)
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_ALPHA_ADVANTAGE)
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_YAHOO)
    #_quote_engine.get_historical_price(tickers, settings.constants.HISTORICAL_QUOTE_DATA_SRC_CNBC)
    # print(_quote_engine.get_historical_price(tickers, source = settings.constants.EODHISTORICALDATA).tickers_result)
    #russell_engine = russell.engine()
    #russell_engine.get_russell_components(upload_to_db = True)
    #russell_2000_engine = russell_2000.engine()
    #russell_2000_engine.get_russell_components(upload_to_db = True)

    #sravz_assets.upload_assets()

    #price_engine = price.engine()
    #price_engine.get_current_price(upload_to_db = True)
    #price_engine.get_current_price_cnbc(upload_to_db = True)

    #tengine = treasury_engine()
    #tengine.upload_quandl_to_s3(settings.constants.quotes['treasury_real_longterm_rate'], 'treasury_real_longterm_rate')
    #tengine.upload_quandl_to_s3(settings.constants.quotes['treasury_real_yieldcurve_rate'], 'treasury_real_yieldcurve_rate')
    #tengine.upload_quandl_to_s3(settings.constants.quotes['treasury_bill_rate'], 'treasury_bill_rate')
    #tengine.upload_quandl_to_s3(settings.constants.quotes['treasury_long_term_rate'], 'treasury_long_term_rate')

    #dj30_components_engine = dj30.engine()
    #dj30 = dj30_components_engine.get_dj30_components(upload_to_db = True)
    # print(dj30)
    # bse_sensex_components_engine = bse_sensex_components.engine()
    # bse_components = bse_sensex_components_engine.get_bse_sensex_components(upload_to_db=True)
    # print(bse_components)
    # ftse_bursa_malaysia_engine = ftse_bursa_malaysia.engine()
    # ftse_bursa_malaysia_components = ftse_bursa_malaysia_engine.get_bursa_malaysia_components(upload_to_db=True)
    # print(ftse_bursa_malaysia_components)
    # ftse_uk_100_engine = ftse_uk_100.engine()
    # ftse_uk_100_components = ftse_uk_100_engine.get_ftse_uk_100_components(upload_to_db=True)
    # print(ftse_uk_100_components)
    # dax_engine = dax.engine()
    # dax_components = dax_engine.get_dax_components(upload_to_db=True)
    # print(dax_components)
    # cac40_engine = cac40.engine()
    # cac40_components = cac40_engine.get_cac40_components(upload_to_db=True)
    # print(cac40_components)
    # obx_engine = obx.engine()
    # obx_components = obx_engine.get_obx_components(upload_to_db=True)
    # print(obx_components)
    # ta125_engine = ta125.engine()
    # ta125_components = ta125_engine.get_ta125_components(upload_to_db=True)
    # print(ta125_components)
    #xao_components_engine = all_ordinaires.engine()
    #xao_components = xao_components_engine.get_xao_components(upload_to_db = True)
    #xao_components_engine.upload_xao_components_to_db(xao_components)

    #price_engine = price.engine()
    # price_engine.upload_end_of_day_cnbc_price_to_mdb()

    # print(is_user_asset('fut_gold'))
    # print(is_user_asset('testuser-daily_MSFT.1.csv-1548287870518'))
    # helper.empty_cache_if_new_day()

    # pcae = pca.engine()
    # time_frame_in_years = 10
    # sravzids = ['fut_gold', 'fut_silver']
    #pcae.get_scatter_plot_daily_return(sravzids, time_frame_in_years, upload_to_aws = True, device = settings.constants.DEVICE_TYPE_MOBILE)
    #pcae.get_pca_components(sravzids, upload_to_aws = True)
    #pcae.get_pca_components_vs_index_returns(sravzids, upload_to_aws = False)
    #pcae.get_scatter_plot_daily_return(['index_spx'], time_frame_in_years, upload_to_aws = True, device = settings.constants.DEVICE_TYPE_MOBILE)

    #marketwatchengine = marketwatch.engine()
    #print(marketwatchengine.get_quotes(tickers=['D', 'SPX']))

    #indexquotesengine = index_quotes_engine()
    #print(indexquotesengine.get_us_index_quotes(upload_to_db = True))
    #print(indexquotesengine.get_world_index_quotes(upload_to_db=True))
    #print(indexquotesengine.get_eodhistoricaldata_index_quotes(upload_to_db = True))

    #index_historical_quotes_engine = index_historical_quotes.engine()
    # #index_historical_quotes_engine.get_us_index_historical_quotes(upload_to_db=True)
    #index_historical_quotes_engine.get_world_idx_quotes(upload_to_db=True)

    # pcae = pca.engine()
    # stock_rets = pcae.get_percent_daily_returns(['fut_gold']).tz_localize('UTC', level=0)
    # benchmark_rets = pcae.get_percent_daily_returns(['idx_us_gspc']).tz_localize('UTC', level=0)
    # print(f"stock_rets count: ${stock_rets.count()} - bench mark returns count: ${benchmark_rets.count()}")
    # fig = pf.create_returns_tear_sheet(stock_rets.squeeze(), benchmark_rets=benchmark_rets.squeeze(), return_fig = True)
    # file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
    # fig.savefig(file_path)
    # plt.close(fig)
    #pcae.create_portfolio_pca_report(['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme'])

    # ce = charts.engine()
    # ce.get_combined_charts(['stk_us_cvna', 'stk_us_twlo'], upload_to_aws=True, device='pc') #fut_gold', 'fut_silver'], upload_to_aws=True, device='pc')
    # print(ce.get_combined_chart_image(['fut_us_gc'], upload_to_aws=True, device='mobile'))
    # re = risk.engine()
    # re.get_returns_tear_sheet('fut_gold') #idx_us_gspc')
    #re.get_bayesian_tear_sheet('fut_gold')
    #re.get_stocker_tear_sheet('crypto_ada_usd', 'CHART_TYPE_CREATE_PROPHET_MODEL')

    #utile = util.Util()
    #print(utile.get_portfolio_assets('teatss', '5f232d744f925716f94b5eee'))
    #print(utile.get_portfolio_assets_weights('teatss', '5f232d744f925716f94b5eee'))

    #pe = portfolio.engine()
    #print(pe.get_portfolio_assets_daily_returns('teatss', '5f232d744f925716f94b5eee'))
    # print(pe.get_portfolio_daily_returns('teatss', '5f232d744f925716f94b5eee'))
    #print(pe.get_portfolio_daily_returns(None, None, portfolio_assets= ['fut_gold', 'fut_oil']))
    #print(pe.get_portfolio_assets_cummulative_daily_returns('GoldAndOil1', '5af375146d157413f4945e1b'))
    #print(pe.create_portfolio_returns_tear_sheet('goldandspx', '597d79c46d15740af8fa884a'))
    #print(pe.portfolio_returns_timeseries_analysis('GoldAndOil1', '5af375146d157413f4945e1b'))
    #print(pe.get_stocker_tear_sheet_predict_future('GoldAndOil1', '5af375146d157413f4945e1b'))
    # print(pe.get_stocker_tear_sheet_create_prophet_model('GoldAndOil1', '5af375146d157413f4945e1b'))
    #print(pe.get_correlation_analysis_tear_sheet('GoldAndOil', '5af375146d157413f4945e1b'))

    #te = timeseries.engine()
    # te.get_ts_analysis('fut_spx')

    #mwe = quotes_providers.marketwatch.engine()
    # print(mwe.get_world_index_quotes())

    #mce = moneycontrol.engine()
    # print(mce.get_world_index_quotes())

    #ye = yahoo.engine()
    # print(ye.get_world_index_quotes())
    # print(ye.get_historical_quotes('FB'))

    # index_historical_quotes_engine = index_historical_quotes.engine()
    # we = webcrawler.engine()
    # df = we.get_csv_data_from_url(None, source = 'yahoo', ticker = '%5EN100')
    # print(index_historical_quotes_engine.transform_yahoo_quote_data(df))

    # we = webcrawler.engine()
    # df = we.get_csv_data_from_url('https://iss.moex.com/iss/history/engines/stock/markets/index/securities/IMOEX.csv?iss.only=history&iss.dp=comma&iss.df=%25Y-%25m-%25d&iss.tf=%25H%3A%25M%3A%25S&iss.dtf=%25Y.%25m.%25d%20%25H%3A%25M%3A%25S&iss.json=extended&callback=JSON_CALLBACK&from=2019-04-13&till=2019-05-14&lang=en&limit=100&start=0&sort_order=TRADEDATE&sort_order_desc=desc&_=1557882614079')
    # print(df)

    # ecocal_engine = ecocal.engine()
    # ecocal_engine.get_current_week_eco_cal_from_web(upload_to_db = True)

    #curr_eng = currency_quotes_engine()
    #curr_eng.get_currency_quotes(upload_to_db=True)
    # curr_eng.get_currency_quotes(upload_to_db=True, db_type='historical')
    # curr_eng.get_historical_currency_quotes(upload_to_db=True, ndays_back=15)

    #rates_eng = rates_quotes_engine()
    #rates_eng.get_rate_quotes(upload_to_db=True)
    #rates_eng.get_historical_rates_quotes(upload_to_db=True)

    #crypto_engine = crytp_quotes_engine()
    # crypto_engine.get_historical_crypto_quotes(upload_to_db=True)
    #crypto_engine.get_crypto_quotes(upload_to_db=True)
    # crypto_hash_e = crytp_hash_engine()
    # crypto_hash_e.get_historical_crypto_hash_rate(upload_to_db = True, ndays_back=15)
    #crypto_engine.get_eodhistoricaldata_crypto_quotes(upload_to_db=True)
    #crypto_engine.get_eodhistoricaldata_historical_crypto_quotes(upload_to_db=True)

    # Upload historical data
    #cqe = commodities_quotes_engine()
    # cqe.upload_all_quandl_to_db(sravzids=None, ndays_back=15)
    #cqe.get_eodhistoricaldata_live_future_quotes()
    # cqe.get_eodhistoricaldata_historical_future_quotes()

    #iqe = index_historical_quotes.engine()
    #iqe.get_us_index_historical_quotes(
    #     tickers=['idx_us_gspc'], upload_to_db=True, ndays_back=None)
    #iqe.get_world_idx_quotes(upload_to_db=True, ndays_back=None)

    #cqe = currency_quotes_engine()
    # cqe.get_historical_currency_quotes(upload_to_db=True, ndays_back=15)
    #cqe.get_eodhistoricaldata_historical_currency_quotes(upload_to_db=True)
    #cqe.get_eodhistoricaldata_live_currency_quotes(upload_to_db=True)

    # crqe = crytp_quotes_engine()
    # crqe.get_historical_crypto_quotes(upload_to_db=True, ndays_back=15)

    #rqe = rates_quotes_engine()
    #rqe.get_historical_rates_quotes(upload_to_db=True, ndays_back=settings.constants.NDAY_BACK_FOR_HISTORICAL_QUOTES)
    #rqe.get_historical_mortgage_rates_quotes(upload_to_db=True)
    # print(rqe.get_mortgage_rates_quotes(upload_to_db=True))


    #stock_rets = pcae.get_percent_daily_returns(
    #    ['stk_us_fb']).tz_localize('UTC', level=0)
    #benchmark_rets = pcae.get_percent_daily_returns(
    #    ['idx_us_gspc']).tz_localize('UTC', level=0)
    #out_of_sample = stock_rets.index[-40]
    #fig = tears.create_bayesian_tear_sheet(stock_rets.squeeze(
    #), return_fig=True,
    #live_start_date=out_of_sample)
    #file_path = helper.util.get_temp_file()
    #fig.savefig(file_path)
    #plt.close(fig)

    # amazon = stocker.Stocker('fut_gold')
    # # model, model_data, file_path = amazon.create_prophet_model(days=90)
    # # file_path = amazon.evaluate_prediction()
    # # file_path = amazon.changepoint_prior_analysis(changepoint_priors=[0.001, 0.05, 0.1, 0.2])
    # print(amazon.changepoint_prior_validation(start_date='2016-01-04', end_date='2017-01-03', changepoint_priors=[0.001, 0.05, 0.1, 0.2]))
    # # amazon.changepoint_prior_validation(start_date='2016-01-04', end_date='2017-01-03', changepoint_priors=[0.15, 0.2, 0.25,0.4, 0.5, 0.6])
    # amazon.changepoint_prior_scale = 0.5
    # # amazon.evaluate_prediction()
    # file_path = amazon.predict_future(days=100)
    #file_pah = amazon.predict_future()

    #fig = stocker_tears.create_stocker_tear_sheet('fut_gold', stocker_tears.CHART_TYPE_CREATE_PROPHET_MODEL)
    #fig = stocker_tears.create_stocker_tear_sheet('fut_gold', stocker_tears.CHART_TYPE_EVALUATE_PREDICTION)
    #fig = stocker_tears.create_stocker_tear_sheet('fut_gold', stocker_tears.CHART_TYPE_CHANGE_POINT_PRIOR_ANALYSIS)
    # fig = stocker_tears.create_stocker_tear_sheet('fut_gold', stocker_tears.CHART_TYPE_CHANGE_POINT_PRIOR_VALIDATION)
    #fig = stocker_tears.create_stocker_tear_sheet('fut_gold', stocker_tears.CHART_TYPE_EVALUATE_PREDICTION_WITH_CHANGE_POINT)
    #fig = stocker_tears.create_stocker_tear_sheet('fut_gold', stocker_tears.CHART_TYPE_PREDICT_FUTURE)
    #file_path = helper.util.get_temp_file()
    #fig.savefig(file_path)
    #plt.close(fig)

    # index_componentse = index_components.engine()
    # #print(index_componentse.get_index_components_df('idx_us_gspc'))
    # print(index_componentse.get_index_components_grouped_by_sector_df('idx_us_gspc'))
    #print(index_componentse.get_index_components_grouped_by_sector_df('idx_us_rua'))
    # print(index_componentse.get_eod_index_components_grouped_by_sector_df('idx_us_gspc'))


    #chartse = charts.engine()
    #chartse.get_all_index_components_bar_charts()
    # chartse.get_crypto_tearsheet(None)
    #chartse.get_eod_all_index_components_bar_charts()

    #mdbe_historical = mdb.engine(database_name='historical', database_url='historical_url')
    #mdbe_historical.load_csv('/Users/fd98279/Documents/CSVForDate.csv', 'idx_in_1')
    #mdbe_realtime = mdb.engine()
    #print(mdbe_realtime.get_collection_as_df(util.settings.constants.WORLD_CAPITALS_COLLECTION))


    #helper.concat_n_images(['/tmp/ef4c93be304c44878da40196f4d9e5c0.png',
    #                             '/tmp/5b19aa711a38467b80cb388165520aec.png'])

    #vengine = vix_quotes_engine()
    #vengine.get_historical_vix_quotes(upload_to_db=True)
    # vengine.get_vix_quotes(None, upload_to_db=True)

    #eodengine = eodhistoricaldata.engine()
    #eodengine.get_list_of_indexes()
    #eodengine.get_list_of_currencies()

    #sravz_assets_indices.upload_assets()
    #sravz_assets_indices.upload_index_components_to_s3()
    #sravz_assets_indices.upload_index_components_to_mdb()
    #sravz_assets_crypto.upload_assets()
    #sravz_assets_forex.upload_assets()
    # sravz_assets_exchanges.upload_assets()
    #sravz_assets_exchanges.upload_world_locations()
    #sravz_assets_exchanges.upload_world_capitals()
    #sravz_assets_exchanges.upload_world_major_indices_names()
    #sravz_assets_exchanges.upload_exchange_components_to_s3()
    #sravz_assets_exchanges.upload_exchange_components_to_mdb()
    #sravz_assets_exchanges.upload_etfs_list()
    #sravz_assets_exchanges.upload_futures_list_to_mdb()
    #sravz_assets_exchanges.upload_option_tickers()
    # sravz_assets_exchanges.upload_exchange_symbol_list()

    #awse = aws.engine()
    #print(awse.download_quotes_from_s3('treasury_real_longterm_rate'))

    #dashboard_engine = dasboard_upload_from_db_to_s3.engine()
    #dashboard_engine.upload()

    #bonde = bond_historical_quotes.engine()
    #bonde.get_eodhistoricaldata_historical_bond_quotes()