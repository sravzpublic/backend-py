#!/usr/bin/env python
import datetime, time
from src.services import mdb
from src.util import logger, helper, settings
from src.services import aws

'''
        {'etf': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100,'value': 33590481, 'change': '-5', 'change_pct': '-5'}],
        'commodities': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '5'}],
        'indexes': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '5'}],
        'currencies': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '-5'}],
        'mutualfunds': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '-5'}],
        'rates': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '0'}],
        'earnings': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '0'}],
        'fundamentals': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '0'}],
        'rss_feeds': [{'text': 'Title The UK\'s Covid vaccine program and delta surge means it\'s now a test case for the world'}],
        'portfolios': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '0'}],
        'mortgagerates': [{'sravz_id': 'test1', 'region': '', 'country': 'US', 'lat': 40, 'lon': -100, 'value': 33590481, 'change': '-5', 'change_pct': '0'}],
        'charts': [
          {'link': '/asset/all', 'linkParams': '{\"sravzIds\":\"fut_gold\"}', 'linkText': 'Gold Future'},
          {'link': '/asset/all', 'linkParams': '{\"sravzIds\":\"fut_silver\"}', 'linkText': 'Silver Future'},
        ],
        'economiccalander': [
          {'link': '/economics/calendar', 'linkParams': '{\"autoFetch\": \"true\"}', 'linkText': 'US - Current Week'},
        ],
        'analytics': [
          {'link': '/analytics/all', 'linkParams': '{\"analyticsType\":\"PCA Analysis\",\"assetType\":\"portfolio\"}', 'linkText': 'PCA Analysis'},
          {'link': '/analytics/all', 'linkParams': '{\"analyticsType\":\"Prophet Model Analysis\", \"assetType\": \"asset\"}', 'linkText': 'Prophet Model Analysis'},
          {'link': '/analytics/all', 'linkParams': '{\"analyticsType\":\"Pyfolio Returns Analysis\", \"assetType\": \"asset\"}', 'linkText': 'Pyfolio Returns Analysis'},
          {'link': '/analytics/all', 'linkParams': '{\"analyticsType\":\"Rolling Statistics\", \"assetType\": \"asset\"}', 'linkText': 'Rolling Statistics'},
          {'link': '/analytics/all', 'linkParams': '{\"analyticsType\":\"Time Series Analysis\", \"assetType\": \"asset\"}', 'linkText': 'Time Series Analysis'},
          {'link': '/analytics/all', 'linkParams': '{\"analyticsType\":\"Covariance Analysis\",\"assetType\":\"portfolio\"}', 'linkText': 'Covariance Analysis'},
        ]
    };
'''

class engine(object):
    """Gets quotes to be displayed on the dashboard"""

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.awse = aws.engine()

    def upload(self):
        no_of_items = 5
        _logger = logger.RotatingLogger(__name__).getLogger()
        mdb_engine = mdb.engine()
        dashboard = {}
        quote_type_to_sravz_id_mapping = {
            'currency': ['forex_chfusd', 'forex_eurusd', 'forex_usdcny', 'forex_usdjpy', 'forex_usdinr'],
            'rates': ['int_usa_usd', 'int_gbr_gbp', 'int_chn_cny', 'int_ecb_eur', 'int_che_chf'],
            'crypto': ['crypto_btc_usd', 'crypto_eth_usd', 'crypto_usdt_usd', 'crypto_bnb_usd', 'crypto_doge_usd'],
            'stocks': ['stk_us_aapl', 'stk_us_fb', 'stk_us_nflx', 'stk_us_msft', 'stk_us_googl'],
            'index': ['idx_us_gspc', 'idx_us_ndx', 'idx_us_ixic', 'idx_us_dji', 'idx_us_rui'],
            'futures': ['fut_us_gc', 'fut_us_sp', 'fut_us_nq', 'fut_us_ym', 'fut_us_qm'],
            'mortgage': ['int_usa_usd_dcu_variable_10 Years Fixed', 'int_usa_usd_dcu_variable_15 Years Fixed', 'int_usa_usd_dcu_variable_20 Years Fixed', 'int_usa_usd_dcu_variable_30 Years Fixed', 'int_usa_usd_dcu_variable_Jumbo 30 Years Fixed']
        }
        for quote_type in ['currency', 'rates', 'crypto', 'stocks', 'index', 'futures','mortgage']:
            self.logger.info(f"Processing quote_type {quote_type}")
            quotes = mdb_engine.get_collection_items(
                'quotes_{0}'.format(quote_type), find_clause={"SravzId": { "$in": quote_type_to_sravz_id_mapping.get(quote_type)}},
                exclude_clause = {'_id': False}, iterator=False, cache=False)
            dashboard[quote_type] = quotes

        asset_type_to_sravz_id_mapping = {
            'etf': ['etf_us_QLD', 'etf_us_TQQQ', 'etf_us_SQQQ', 'etf_us_VOO', 'etf_us_VGT'],
        }
        for asset_type in ['etf']:
            self.logger.info(f"Processing asset_type {asset_type}")
            assets = mdb_engine.get_collection_items(
                'assets_{0}'.format(asset_type), find_clause={"SravzId": { "$in": asset_type_to_sravz_id_mapping.get(asset_type)}},
                exclude_clause = {'_id': False},
                iterator=False, cache=False)
            dashboard[asset_type] = assets

        dashboard['mutualfunds'] = mdb_engine.get_collection_items(settings.constants.EXCHANGE_SYMBOLS_COLLECTION,
        exclude_clause = {'_id': False},
        find_clause={"SravzId": { "$in": ['FUND_us_FBGRX', 'FUND_us_FSPTX', 'FUND_us_FZIIX', 'FUND_us_FZAPX', 'FUND_us_FZILX']}},
        iterator=False, cache=False)

        earnings = mdb_engine.get_collection_items('earnings',
        find_clause={"report_date": { "$gte": datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"),'%Y-%m-%d')}, 'code' : { "$regex": '.US'}},
        exclude_clause = {'_id': False},
        iterator=False, cache=False)
        if earnings:
            dashboard['earnings'] = earnings[:no_of_items]
        else:
            dashboard['earnings'] = []

        rss_feeds = mdb_engine.get_collection_items('rss_feeds',
        exclude_clause = {'_id': False},
        find_clause={"datetime": { "$gte": datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"),'%Y-%m-%d')}},
        iterator=False, cache=False)
        if rss_feeds:
            dashboard['rss_feeds'] = rss_feeds[:no_of_items]
        else:
            dashboard['rss_feeds'] = []

        portfolios = mdb_engine.get_collection_items('portfolios',
        exclude_clause = {'_id': False},
        iterator=False, cache=False)
        if rss_feeds:
            dashboard['portfolios'] = portfolios[:no_of_items]
        else:
            dashboard['portfolios'] = []

        portfolios = mdb_engine.get_collection_items('portfolios',
        exclude_clause = {'_id': False, 'portfolioassets': False, 'user': False},
        iterator=True, cache=False, limit = no_of_items)
        if portfolios:
            dashboard['portfolios'] = list(portfolios)
        else:
            dashboard['portfolios'] = []

        self.logger.info(dashboard)

        if dashboard:
            self.awse.upload_data_to_s3(dashboard, settings.constants.SRAVZ_DATA_S3_BUCKET, 'dashboard.json')
            self.logger.info("Dashboard uploaded to s3")
        else:
            self.logger.warn(f"Dashbord is empty {dashboard}")
