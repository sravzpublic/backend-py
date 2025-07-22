import platform
import datetime
import os


class constants(object):
    """description of class"""
    # Fake Data
    development = read_from_file = platform.system(
    ) in ['Windows', 'Darwin'] or os.environ.get('NODE_ENV') == 'vagrant'
    fake_data_directory = 'C:\\\\workspace\\sravz\\backend-py\\data\\' if platform.system(
    ) == 'Windows' else '/home/vagrant/sravz/development/backend-py/data/'
    windows_log_file = "C:\\\\temp\\sravz_jobs.log"
    linux_log_file = os.environ.get(
        'ENV_LOG_FILE_NAME') or "/tmp/sravz_jobs.log"

    disk_cache = {
        'dev':  {'dir': "c:/tmp/sravzdiskcache", 'timeout': 60, 'shards': 8},
        'prod': {'dir': "/tmp/sravzdiskcache", 'timeout': 60, 'shards': 8}
    }
    # Bucket config
    bucket_name = 'sravz-commodities'
    analytics_bucket_name = 'sravz-analytics'
    historical_rolling_stats_bucket_name = 'sravz-historical-rolling-stats'
    pca_scatter_plot_bucket_name = 'sravz-scatter-plot-pca'
    pca_components_bucket_name = 'sravz-components-pca'
    pca_covariance_matrix_bucket_name = 'sravz-covariance-matrix-pca'
    charts_bucket_name = 'sravz-charts'
    risk_stats_bucket_name = 'sravz-risk-stats'
    sravz_monthly_bucket_name = 'sravz-monthly'
    AWS_BUCKETS = [bucket_name, analytics_bucket_name, historical_rolling_stats_bucket_name,
                   pca_scatter_plot_bucket_name, pca_components_bucket_name, pca_covariance_matrix_bucket_name,
                   charts_bucket_name, risk_stats_bucket_name]
    AWS_USER_ASSETS_BUCKET = 'sravz-user-assets'
    AWS_PRICE_DF_STATS = 'sravz-price-df-stats'
    DASK_SCHEDULER_HOST_NAME = os.environ.get('DASK_SCHEDULER_HOST_NAME') or 'scheduler'

    DB_TYPE_LIVE = 'live'
    DB_TYPE_HISTORICAL = 'historical'

    NDAY_BACK_FOR_HISTORICAL_QUOTES = int(os.environ.get('NDAY_BACK_FOR_HISTORICAL_QUOTES')) if os.environ.get('NDAY_BACK_FOR_HISTORICAL_QUOTES') else 15
    QUANDL_API_KEY = os.environ.get('QUANDL_API_KEY') or "{{QUANDL_API_KEY}}"

    NSQ_MESSAGE_PROCESSING_TIMEOUT_SECS = 300

    # Stats constants
    number_of_years = 10
    df_test_column_index = 1
    mongobd_connection_string = {
        'dev': {
            'url': os.environ.get('MONGOLAB_URI'),
            'database': 'sravz',
            'historical_url': os.environ.get('MONGOLAB_SRAVZ_HISTORICAL_URI'),
            'historical': 'sravz_historical'
        },
        'prod': {
            'url': os.environ.get('MONGOLAB_URI'),
            'database': 'sravz',
            'historical_url': os.environ.get('MONGOLAB_SRAVZ_HISTORICAL_URI'),
            'historical': 'sravz_historical'
        }
    }
    kafka_settings = {
        'dev': {
            'broker_list': 'vagrant.sravz.com:9092'
        },
        'prod': {
            'broker_list': 'kafkadev.sravz.com:9092'
        }
    }
    # All quotes urls
    quotes = {
        'commodities': {
            'url': 'http://www.investing.com/commodities/real-time-futures'
        },
        'cnbc_commodities_urls':
        [
            "http://quote.cnbc.com/quote-html-webservice/quote.htm?callback=webQuoteRequest&symbols=%40{0}&symbolType=symbol&requestMethod=quick&exthrs=1&extMode=&fund=1&entitlement=0&skipcache=&extendedMask=1&partnerId=2&output=jsonp&noform=1".format(
                symbol)
            for symbol in [
                'GC.1', 'SI.1', 'HG.1', 'PL.1', 'PA.1',
                'CL.1', 'LCO.1', 'NG.1', 'RB.1', 'HO.1', 'AC.1', 'UXX.1',
                'W.1', 'C.1', 'SB.1', 'S.1', 'BO.1', 'SM.1', 'OJ.1', 'KC.1', 'CC.1', 'RR.1', 'O.1', 'DA.1', 'CT.1', 'LB.1',
                'LC.1', 'FC.1', 'LH.1',
                'DX.1', 'JY.1', 'BP.1', 'AD.1', 'CD.1', 'SF.1',
                'DJ.1', 'SP.1', 'ND.1', 'MD.1', 'SMC.1',
                'US.1', 'TY.1', 'TU.1', 'GE.1', 'URO.1']
        ],
        'quandl_commodities_urls': [
            ("fut_gold", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_GC1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_silver", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_SI1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_platinum",
             "https://www.quandl.com/api/v3/datasets/CHRIS/CME_PL1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_palladium", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_PA1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_copper", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_HG1.json?api_key=My4TXrS2R1VeXt-shsYD"),

            ("fut_oil", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_CL1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_brent", "https://www.quandl.com/api/v3/datasets/CHRIS/ICE_B1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_natgas", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_NG1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_ulsdho", "https://www.quandl.com/api/v3/datasets/SCF/CME_HO1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_rbobgas", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_RB1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_ethanol", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_EH1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_uranium", "https://www.quandl.com/api/v3/datasets/ODA/PURAN_USD.json?api_key=My4TXrS2R1VeXt-shsYD"),

            ("fut_wheat", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_W1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_corn", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_C1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_sugar", "https://www.quandl.com/api/v3/datasets/CHRIS/ICE_SB1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_soybean", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_S1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_soyoil", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_BO1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_soymeal", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_SM1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_ojfut", "https://www.quandl.com/api/v3/datasets/CHRIS/ICE_OJ1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_coffee", "https://www.quandl.com/api/v3/datasets/CHRIS/ICE_KC1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_cocoa", "https://www.quandl.com/api/v3/datasets/CHRIS/ICE_CC1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_roughrice", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_RR1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_oats", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_O1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_milk", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_DK1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_cotton", "https://www.quandl.com/api/v3/datasets/CHRIS/ICE_CT1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_lumber", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_LB1.json?api_key=My4TXrS2R1VeXt-shsYD"),

            ("fut_lvcattle", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_LC1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_fdcattle", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_FC1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_leanhogs", "https://www.quandl.com/api/v3/datasets/CHRIS/CME_LN1.json?api_key=My4TXrS2R1VeXt-shsYD"),

            ("fut_usdidxfut", "https://www.quandl.com/api/v3/datasets/SCF/ICE_DX1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_usdjpyfut", "https://www.quandl.com/api/v3/datasets/SCF/CME_JY1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_gbpusdfut", "https://www.quandl.com/api/v3/datasets/SCF/CME_BP1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_audusdfut", "https://www.quandl.com/api/v3/datasets/SCF/CME_AD1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_usdcadfut", "https://www.quandl.com/api/v3/datasets/SCF/CME_CD1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_usdchffut", "https://www.quandl.com/api/v3/datasets/SCF/CME_SF1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),

            ("fut_dowfut", "https://www.quandl.com/api/v3/datasets/SCF/CME_DJ1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_s&amp;pfut', "https://www.quandl.com/api/v3/datasets/SCF/CME_SP1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_nasfut', "https://www.quandl.com/api/v3/datasets/CHRIS/CME_ND1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_s&amp;pmidmini',
             "https://www.quandl.com/api/v3/datasets/CHRIS/CME_ND1.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_s&amp;p600mini',
             "https://www.quandl.com/api/v3/datasets/SCF/CME_ES1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),

            ('fut_us30yrfut', "https://www.quandl.com/api/v3/datasets/SCF/CME_US1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_us10yrfut', "https://www.quandl.com/api/v3/datasets/SCF/CME_TY1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_us2yfut', "https://www.quandl.com/api/v3/datasets/SCF/CME_TU1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_euro$3m', "https://www.quandl.com/api/v3/datasets/SCF/CME_ED1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ('fut_eurusdfut', "https://www.quandl.com/api/v3/datasets/SCF/CME_ED1_FW.json?api_key=My4TXrS2R1VeXt-shsYD"),

            # Live quotes not available, these are LME quotes, use link: http://www.lme.com/metals/non-ferrous/zinc/
            ("fut_aluminum_na_na_usd_lme",
             "https://www.quandl.com/api/v3/datasets/LME/PR_AL.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_zinc_na_na_usd_lme",
             "https://www.quandl.com/api/v3/datasets/LME/PR_ZI.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_lead_na_na_usd_lme",
             "https://www.quandl.com/api/v3/datasets/LME/PR_PB.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_nickel_na_na_usd_lme",
             "https://www.quandl.com/api/v3/datasets/LME/PR_NI.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_copper_na_na_usd_lme",
             "https://www.quandl.com/api/v3/datasets/LME/PR_CU.json?api_key=My4TXrS2R1VeXt-shsYD"),
            ("fut_tin_na_na_usd_lme",
             "https://www.quandl.com/api/v3/datasets/LME/PR_TN.json?api_key=My4TXrS2R1VeXt-shsYD"),
        ],
            # Housing Constants
            'int_nahb_forecast': 'https://www.quandl.com/api/v3/datasets/NAHB/INTRATES.json?api_key=My4TXrS2R1VeXt-shsYD',
            'treasury_real_longterm_rate': 'https://www.quandl.com/api/v3/datasets/USTREASURY/REALLONGTERM.json?api_key=My4TXrS2R1VeXt-shsYD',
            'treasury_real_yieldcurve_rate': 'https://www.quandl.com/api/v3/datasets/USTREASURY/REALYIELD.json?api_key=My4TXrS2R1VeXt-shsYD',
            'treasury_bill_rate': 'https://www.quandl.com/api/v3/datasets/USTREASURY/BILLRATES.json?api_key=My4TXrS2R1VeXt-shsYD',
            'treasury_long_term_rate': 'https://www.quandl.com/api/v3/datasets/USTREASURY/LONGTERMRATES.json?api_key=My4TXrS2R1VeXt-shsYD',
    }
    # Used for stationarity test of commodities
    all_commodities = [{'name': 'gold',
                        'price_url': "https://www.quandl.com/api/v3/datasets/CHRIS/CME_GC1.json?api_key=My4TXrS2R1VeXt-shsYD",
                        'price_lambda': lambda data: data['dataset']['data'],
                        'price_column_lambda': lambda data:data['dataset']['column_names']
                        },
                       {'name': 'silver',
                        'price_url': "https://www.quandl.com/api/v3/datasets/LBMA/SILVER.json?api_key=My4TXrS2R1VeXt-shsYD",
                           'price_lambda': lambda data: data['dataset']['data'],
                           'price_column_lambda': lambda data:data['dataset']['column_names']
                        },
                       {
        'name': 'platinum',
                           'price_url': "https://www.quandl.com/api/v3/datasets/LPPM/PLAT.json?api_key=My4TXrS2R1VeXt-shsYD",
                           'price_lambda': lambda data: data['dataset']['data'],
                           'price_column_lambda': lambda data:data['dataset']['column_names']
    },
        {
        'name': 'palladium',
                           'price_url': "https://www.quandl.com/api/v3/datasets/LPPM/PALL.json?api_key=My4TXrS2R1VeXt-shsYD",
                           'price_lambda': lambda data: data['dataset']['data'],
                           'price_column_lambda': lambda data:data['dataset']['column_names']
    }]

    commodities_to_exclude = ['fut_LondonGasOil']

    all_currency = {'fut_XAU/USD_NA_NA_usd_cme':
                    {'name': 'xauusd',
                     'url': "http://www.exchangerates.org.uk/commodities/XAU-USD-history.html#USD-history-table",
                     'table_selector': {"id": "hist"}
                     }
                    }
    snp = {
        'components_url': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
        'table_class': 'wikitable sortable',
        'historical_quotes_url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/SPX?MOD_VIEW=page&ticker=SPX&country=US&exchange=&instrumentType=INDEX&num_rows=7029.958333333333&range_days=7029.958333333333&startDate=01%2F15%2F1970&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                              datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                              datetime.datetime.now().year),
        'historical_quotes_table_class': 'cr_dataTable',
    }
    russle3000 = {
        'components_url': 'https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1467271812596.ajax?fileType=csv&fileName=IWV_holdings&dataType=fund'
    }
    russle2000 = {
        'components_url': 'https://www.ishares.com/us/products/239710/ishares-russell-2000-etf/1467271812596.ajax?tab=all&fileType=json'
    }
    dj30 = {
        'components_url': 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average',
        'table_class': 'wikitable sortable'
    }
    idx_in_1 = {
        'components_url': 'https://en.wikipedia.org/wiki/BSE_SENSEX',
        'table_class': 'wikitable sortable'
    }
    idx_my_fbmklci = {
        'components_url': 'https://en.wikipedia.org/wiki/FTSE_Bursa_Malaysia_KLCI',
        'table_class': 'wikitable sortable'
    }
    idx_uk_ftse = {
        'components_url': 'https://en.wikipedia.org/wiki/FTSE_100_Index',
        'table_class': 'wikitable sortable'
    }
    idx_dx_dax = {
        'components_url': 'https://en.wikipedia.org/wiki/DAX',
        'table_class': 'wikitable sortable'
    }
    idx_fr_cac = {
        'components_url': 'https://en.wikipedia.org/wiki/CAC_40',
        'table_class': 'wikitable sortable'
    }
    idx_xx_osebx = {
        'components_url': 'https://en.wikipedia.org/wiki/OBX_Index',
        'table_class': 'wikitable sortable'
    }
    idx_xx_ta100 = {
        'components_url': 'https://en.wikipedia.org/wiki/TA-125_Index',
        'table_class': 'wikitable sortable'
    }
    # Asset types
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"
    # AWS
    DEFAULT_BUCKET_NAME = "sravz-commodities"
    #DEFAULT_PRICE_KEY = lambda asset_name: 'prices/%s_%s'%(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"), asset_name.replace("/", "").replace(" ", ""))
    DEFAULT_BUCKET_KEY_EXPIRY = datetime.datetime.now() + datetime.timedelta(days=2)
    # Economic Calendar
    YAHOO_ECO_CAL_BASE_URL = 'https://finance.yahoo.com/calendar/economic?day='
    @staticmethod
    def get_default_price_key(asset_name):
        return 'prices/%s_%s' % (asset_name.replace("/", "").replace(" ", ""), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
    HISTORICAL_QUOTE_DATE = '1980-01-01'

    # Do not use this for new functions, use the function in helper.py
    @staticmethod
    def get_stock_ticker_from_sravz_id(SravzId):
        '''
            Get the ticker from the sravz_id
            for stk_us_FB return FB
        '''
        ticker = SravzId.split("_")[2] if "stk" in SravzId else SravzId
        return ticker.lower()

    AWS_CORS_ALLOWED_ORIGINS = ["https://vagrant.sravz.com:3030", "https://portfolio.sravz.com",
                                "https://portfoliodev.sravz.com:8086", "https://*.sravz.com",
                                "http://localhost:3030", "http://localhost:8080"]

    # IOT Constants
    SMARTTHINGS_URL = "https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/7ba1cc7a-2eff-479b-a5c8-29771952bbea/things"

    @staticmethod
    def get_cache_config():
        if constants.development:
            if platform.system() == 'Windows':
                conf = constants.disk_cache['dev']
            else:
                conf = constants.disk_cache['prod']
        else:
            conf = constants.disk_cache['prod']
        return conf

    # URL contains the bucket name, use the prefix as bucket name to separate dev and prod
    CONTABO_BUCKET = 'sravz'
    CONTABO_BUCKET_PREFIX = 'sravz-dev' if os.environ.get('NODE_ENV') == 'vagrant' else 'sravz-production'
    CONTABO_URL = os.environ.get('CONTABO_URL')
    CONTABO_BASE_URL = os.environ.get('CONTABO_BASE_URL')
    CONTABO_KEY = os.environ.get('CONTABO_KEY')
    CONTABO_SECRET = os.environ.get('CONTABO_SECRET')
    IDRIVEE2_BASE_URL = os.environ.get('IDRIVEE2_URL')
    IDRIVEE2_KEY = os.environ.get('IDRIVEE2_KEY')
    IDRIVEE2_SECRET = os.environ.get('IDRIVEE2_SECRET')    
    S3_TARGET_AWS = 's3'
    S3_TARGET_CONTABO = 'contabo'
    S3_TARGET_IDRIVEE2 = 'idrivee2'
    HISTORICAL_QUOTE_DATA_SRC_WSJ = "WSJ"
    HISTORICAL_QUOTE_DATA_SRC_MACROTRENDS = "MacroTrends"
    HISTORICAL_QUOTE_DATA_SRC_INVESTOPEDIA = "Investopedia"
    HISTORICAL_QUOTE_DATA_SRC_STOOQ = "Stooq"
    HISTORICAL_QUOTE_DATA_SRC_TIINGO = "Tiingo"
    ALPHA_ADVANTAGE_API_KEY = "2UXQQ1HO1E1WMHLF"
    HISTORICAL_QUOTE_DATA_SRC_ALPHA_ADVANTAGE = "AlphaAdvantagae"
    HISTORICAL_QUOTE_DATA_SRC_YAHOO = "yahoo"
    HISTORICAL_QUOTE_DATA_SRC_CNBC = "cnbc"
    EODHISTORICALDATA = "EODHISTORICALDATA"
    EODHISTORICALDATA_API_KEY = os.environ.get('EODHISTORICALDATA_API_KEY') or "{{EODHISTORICALDATA_API_KEY}}"
    EODHISTORICALDATA_API_KEY2 = os.environ.get('EODHISTORICALDATA_API_KEY2') or "{{EODHISTORICALDATA_API_KEY2}}"
    DARQUBE_API_TOKEN = os.environ.get('DARQUBE_API_TOKEN')
    TICKER_TYPE_FUTURE = 'fut_'
    TICKER_TYPE_STOCK = 'stk_'
    TICKER_TYPE_ETF = 'etf_'
    TICKER_TYPE_MUTUAL_FUND = 'fund_'
    DEVICE_TYPE_PC = 'pc'
    DEVICE_TYPE_MOBILE = 'mobile'
    DEVICE_TYPE_MOBILE_CHARTS_START_DATE = datetime.date(1990, 1, 1)
    DEVICE_TYPE_MOBILE_DELETE_IMAGE_FILES = True

    SRAVZ_ASSET_PREFIX_LEN = 3
    PRICE_SRC_BY_SRAVZ_ID = {
        TICKER_TYPE_MUTUAL_FUND: [S3_TARGET_CONTABO, S3_TARGET_IDRIVEE2],
        TICKER_TYPE_STOCK: [S3_TARGET_CONTABO, S3_TARGET_IDRIVEE2],
        TICKER_TYPE_ETF: [S3_TARGET_CONTABO, S3_TARGET_IDRIVEE2],
    }
    # Charts
    ChartsToDisplayAndAcceptedColumns = {
        # All lower case
        'settle': ['settle', 'last'],
        'change': ['change'],
        'volume': ['volume'],
        'openinterest': ['openinterest'],
        'adjustedclose': ['adjustedclose', 'close']
    }

    # Index list
    US_INDEX = ['SPX', 'RUA', 'DJIA', 'COMP', 'RUT']

    # Country codes
    COUNTRY_CODE_US = 'US'

    # Global Index Source URLs
    GLOBAL_INDEX_SRC = {
        'idx_gdow': {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/GDOW?MOD_VIEW=page&ticker=GDOW&country=US&exchange=&instrumentType=INDEX&num_rows=13968.958333333334&range_days=13968.958333333334&startDate=02%2F09%2F1981&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                    datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                    datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_xx_gdowe':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/GDOWE?MOD_VIEW=page&ticker=GDOWE&country=XX&exchange=&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F09%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_au_xao':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/XAO?MOD_VIEW=page&ticker=XAO&country=AU&exchange=XASX&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_hk_hsi':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/HSI?MOD_VIEW=page&ticker=HSI&country=HK&exchange=XHKG&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F11%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },
        # Not used
        # 'idx_in_1' : 'https://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?strIndex=SENSEX&dtFromDate=01/01/2009&dtToDate={0}%2F{1}%2F{2}'.format(datetime.datetime.now().month,
        #    datetime.datetime.now().day,
        #    datetime.datetime.now().year),
        'idx_in_1':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/1?MOD_VIEW=page&ticker=1&country=IN&exchange=XBOM&instrumentType=INDEX&num_rows=89.95833333333333&range_days=89.95833333333333&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_id_jakidx':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/JAKIDX?MOD_VIEW=page&ticker=JAKIDX&country=ID&exchange=XIDX&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F11%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_jp_nik':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/NIK?MOD_VIEW=page&ticker=NIK&country=JP&exchange=XTKS&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F11%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_my_fbmklci':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/FBMKLCI?MOD_VIEW=page&ticker=FBMKLCI&country=MY&exchange=XKLS&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F11%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                              datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                              datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_lk_asi':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/ASI?MOD_VIEW=page&ticker=ASI&country=LK&exchange=XCOL&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_xx_y9999':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/Y9999?MOD_VIEW=page&ticker=Y9999&country=XX&exchange=XTAI&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_fr_px1':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/PX1?MOD_VIEW=page&ticker=PX1&country=FR&exchange=XPAR&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_dx_dax':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/DAX?MOD_VIEW=page&ticker=DAX&country=DX&exchange=XETR&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_xx_osebx':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/OSEBX?MOD_VIEW=page&ticker=OSEBX&country=XX&exchange=XOSL&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_tr_xu100':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/XU100?MOD_VIEW=page&ticker=XU100&country=TR&exchange=XIST&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_uk_ukx':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/UKX?MOD_VIEW=page&ticker=UKX&country=UK&exchange=&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                  datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                  datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_xx_ta100':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/TA100?MOD_VIEW=page&ticker=TA100&country=XX&exchange=XTAE&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_uk_ftse':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/UKX?MOD_VIEW=page&ticker=UKX&country=UK&exchange=&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                  datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                  datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_fr_cac':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/PX1?MOD_VIEW=page&ticker=PX1&country=FR&exchange=XPAR&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_de_dax':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/DAX?MOD_VIEW=page&ticker=DAX&country=DX&exchange=XETR&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_sg_sgx_nifty':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/STI?MOD_VIEW=page&ticker=STI&country=SG&exchange=XSES&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_tw_taiwan_weighted':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/Y9999?MOD_VIEW=page&ticker=Y9999&country=XX&exchange=XTAI&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_kr_kospi':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/SEU?MOD_VIEW=page&ticker=SEU&country=KR&exchange=XKRX&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_th_set_composite':         {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/SET?MOD_VIEW=page&ticker=SET&country=TH&exchange=XBKK&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },

        'idx_cn_shanghai_composite': {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/SHCOMP?MOD_VIEW=page&ticker=SHCOMP&country=CN&exchange=XSHG&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_eu_bfx': {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/BEL20?MOD_VIEW=page&ticker=BEL20&country=BE&exchange=XBRU&instrumentType=INDEX&num_rows=43553.958333333336&range_days=43553.958333333336&startDate=02%2F11%2F1900&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                          datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_eu_n100': {
            'ticker': '%5EN100',
            'type': 'csv',
            'source': 'yahoo'
        },
        'idx_ca_twii': {
            'ticker': '%5ETWII',
            'type': 'csv',
            'source': 'yahoo'
        },
        'idx_nz_nz50': {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/NZ50GR?MOD_VIEW=page&ticker=NZ50GR&country=NZ&exchange=XNZE&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F14%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_ca_gsptse': {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/GSPTSE?MOD_VIEW=page&ticker=GSPTSE&country=CA&exchange=XTSE&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F14%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                            datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_br_bvsp': {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/BVSP?MOD_VIEW=page&ticker=BVSP&country=BR&exchange=BVMF&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F14%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                        datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                        datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_mx_mxx': {
            'url': 'https://quotes.wsj.com/ajax/historicalpricesindex/7/IPC?MOD_VIEW=page&ticker=IPC&country=MX&exchange=XMEX&instrumentType=INDEX&num_rows=10681.958333333334&range_days=10681.958333333334&startDate=02%2F14%2F1990&endDate={0}%2F{1}%2F{2}&_=1555357263373'.format(datetime.datetime.now().month,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().day,
                                                                                                                                                                                                                                                                                      datetime.datetime.now().year),
            'type': 'html'
        },
        'idx_cl_ipsa': {
            'ticker': '%5EIPSA',
            'type': 'csv',
            'source': 'yahoo'
        },
        'idx_ru_merv': {
            'ticker': '%5EMERV',
            'type': 'csv',
            'source': 'yahoo'
        }
    }

    ST_LOUIS_FRED_API_KEY = os.environ.get(
        'ST_LOUIS_FRED_API_KEY') or "{{ST_LOUIS_FRED_API_KEY}}"

    # Map currency code to SravzID
    # Listed as direct quote. Base Currency/Domestic Currency
    # Base currency = USD
    ST_LOUIS_FRED_CURRENCY_MAP = {
        'DEXUSEU': 'forex_eur_usd',
        'DEXCHUS': 'forex_usd_cny',
        'DEXJPUS': 'forex_usd_jpy',
        'DEXUSUK': 'forex_gbp_usd',
        'DEXCAUS': 'forex_usd_cad',
        'DEXKOUS': 'forex_usd_krw',
        'DEXMXUS': 'forex_usd_mxn',
        'DEXBZUS': 'forex_usd_brl',
        'DEXINUS': 'forex_usd_inr',
        'DEXUSAL': 'forex_aud_usd',
        'DEXVZUS': 'forex_usd_vef',
        'DEXSZUS': 'forex_usd_chf',
        'DEXTHUS': 'forex_usd_thb',
        'DEXMAUS': 'forex_usd_myr',
        'DEXSFUS': 'forex_usd_zar',
        'DEXTAUS': 'forex_usd_tad',
        'DEXHKUS': 'forex_usd_hkd',
        'DEXSDUS': 'forex_usd_sek',
        'DEXSIUS': 'forex_usd_sgd',
        'DEXNOUS': 'forex_usd_nok',
        'DEXUSNZ': 'forex_nzd_usd',
        'DEXDNUS': 'forex_usd_dkk',
        'DEXSLUS': 'forex_usd_lkr',
    }

    ST_LOUIS_FRED_INTEREST_RATES_MAP = {
        'FEDFUNDS': 'int_usa_usd',
    }

    ST_LOUIS_FRED_MORTGAGE_RATES_MAP = {
        'MORTGAGE30US': 'int_usa_usd_30_fixed',
        'MORTGAGE15US': 'int_usa_usd_15_fixed',
        'MORTGAGE5US': 'int_usa_usd_15_1_Adj',
    }

    ST_LOUIS_FRED_VIX_MAP = {
        'GVZCLS': 'vix_gold_eft',
        'VIXCLS': 'vix_vix',
        'VXTYN' : 'vix_10yr_t_note',
        'OVXCLS': 'vix_oil_etf',
        'VXOCLS': 'vix_snp_100',
        'VXFXICLS': 'vix_china_etf',
        'VXEEMCLS': 'vix_emerging_markets_etf',
        'VXNCLS': 'vix_nasdaq_100_etf',
        'EVZCLS': 'vix_euro_currency_etf',
        'VXXLECLS': 'vix_energy_sector_etf',
        'RVXCLS': 'vix_russell_2000',
        'VXDCLS': 'vix_djia',
        'VXSLVCLS': 'vix_silver_etf',
    }

    VIX_QUOTES_URL = 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^'
    VIX_QUOTES_MAP = {
        'vix_gold_eft' : {
            'ticker': 'gvz'
            ''
        },
        'vix_vix' : {
            'ticker': 'vix'
        },
        'vix_10yr_t_note' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^TYVIX',
            'ticker': 'TYVIX'
        },
        'vix_oil_etf' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^OVX',
            'ticker': 'OVX'
        },
        'vix_snp_100' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXO',
            'sravzid': 'vix_snp_100',
            'ticker': 'VXO'
        },
        'vix_china_etf' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXFXI',
            'ticker': 'VXFXI'
        },
        'vix_emerging_markets_etf' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXEEM',
            'ticker': 'VXEEM'
        },
        'vix_nasdaq_100_etf' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXEEM',
            'ticker': 'VXEEM'
        },
        'vix_euro_currency_etf' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXEEM',
            'ticker': 'VXEEM'
        },
        'vix_energy_sector_etf' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXEEM',
            'ticker': 'VXEEM'
        },
        'vix_russell_2000' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXEEM',
            'ticker': 'VXEEM'
        },
        'vix_djia' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXEEM',
            'ticker': 'VXEEM'
        },
        'vix_silver_etf' : {
            'url': 'http://www.cboe.com/delayedquote/advanced-charts?ticker=^VXEEM',
            'ticker': 'VXEEM'
        }
    }

    CRYPTO_QUOTES_URL = {
        'crypto_btc_usd' : 'https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_eth_usd' : 'https://coinmarketcap.com/currencies/ethereum/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_xrp_usd' : 'https://coinmarketcap.com/currencies/ripple/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_bhc_usd' : 'https://coinmarketcap.com/currencies/bitcoin-cash/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_eos_usd' : 'https://coinmarketcap.com/currencies/eos/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_ltc_usd' : 'https://coinmarketcap.com/currencies/litecoin/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_bnb_usd' : 'https://coinmarketcap.com/currencies/binance-coin/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_bsv_usd' : 'https://coinmarketcap.com/currencies/bitcoin-sv/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_xlm_usd' : 'https://coinmarketcap.com/currencies/stellar/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d")),
        'crypto_trx_usd' : 'https://coinmarketcap.com/currencies/tron/historical-data/?start=20130428&end={0}'.format(datetime.datetime.now().strftime("%Y%m%d"))
    }

    CRYPTO_TICKERS = ['btc', 'eth', 'xrp', 'bch', 'eos', 'ltc', 'bnb', 'bsv', 'xlm', 'trx']

    ALL_ORDINARIES = {
        'COMPONENTS_URL' : 'https://www.allordslist.com/',
        'TABLE_CLASS' : 'tableizer-table sortable'
    }

    BITCOIN_HASH_RATE_URL = 'https://api.blockchain.info/charts/hash-rate?scale=1&timespan=all&format=csv'
    ETHEREUM_HASH_RATE_URL = 'https://etherscan.io/chart/hashrate?output=csv'

    RUSSELL_COMPONENTS_COLLECTION_NAME =  'idx_us_rua_components'
    SPX_COMPONENTS_COLLECTION_NAME = 'idx_us_gspc_components'

    # INDEX to use as benchmark
    BENCHMARK_INDEX = 'idx_us_gspc'
    BENCHMARK_INDEX_COLUMN = 'AdjustedClose'
    # Name of collections
    INDEX_ASSETS_COLLECTION = 'assets_index'
    CRYPTO_ASSETS_COLLECTION = 'assets_crypto'
    GBOND_ASSETS_COLLECTION = 'assets_gbond'
    FOREX_ASSETS_COLLECTION = 'assets_forex'
    EXCHANGE_ASSETS_COLLECTION = 'assets_exchange'
    ETF_ASSETS_COLLECTION = 'assets_etf'
    FUTURE_ASSETS_COLLECTION = 'assets_future'
    YTD_US_COLLECTDION = 'ytd_us'
    EXCHANGE_SYMBOLS_COLLECTION = 'assets_exchange_symbols'
    BOND_ASSETS_COLLECTION = 'assets_bond'
    OPTION_ASSETS_COLLECTION = 'assets_option'
    ASSET_COLLECTION_LIST = [INDEX_ASSETS_COLLECTION, CRYPTO_ASSETS_COLLECTION, FOREX_ASSETS_COLLECTION, FUTURE_ASSETS_COLLECTION, BOND_ASSETS_COLLECTION, GBOND_ASSETS_COLLECTION, ETF_ASSETS_COLLECTION, EXCHANGE_SYMBOLS_COLLECTION]
    INDEX_ASSETS_COMPONENTS_COLLECTION = 'assets_index_components'
    EXCHANGE_ASSETS_COMPONENTS_COLLECTION = 'assets_exchange_components'
    WORLD_LOCATIONS_COLLECTION = 'world_locations'
    WORLD_MAJOR_INDICES_COLLECTION = 'world_major_indices'
    WORLD_CAPITALS_COLLECTION = 'world_capitals'
    # 'idx_us_ixic': Nasdaq Composite , 
    # 'idx_us_gspc': S&P 500
    # 'idx_us_w5000': Willshire 5000, 
    # 'idx_us_ruo': Russell 2000 Growth
    # 'idx_us_rut': Russell 2000 
    # 'idx_us_ndx': Nasdaq 100
    # 'idx_us_nya': NYSE Composite
    INDEX_COMPONENTS_QUOTES_TO_UPLOAD = ['idx_us_ixic', 'idx_us_gspc', 'idx_us_w5000', 'idx_us_ruo', 'idx_us_rut', 'idx_us_ndx', 'idx_us_nya']
    # Sravz Data buket
    SRAVZ_DATA_S3_BUCKET = 'sravz-data'
    SRAVZ_HISTORICAL_DATA_PREFIX = "historical"
    SRAVZ_DATA_PREFIX = "sravz"
    SRAVZ_DATA_EOD_INDEX_COMPONENTS_PREFIX = 'eod/fundamentals/index/components/'
    SRAVZ_DATA_EOD_EXCHANGE_COMPONENTS_PREFIX = 'eod/fundamentals/exchange/components/'
    SRAVZ_MONTHLY_EOD_INDEX_COMPONENTS_PREFIX = 'eod/fundamentals/index/components/charts/bar/'
    SRAVZ_MONTHLY_RETURNS_TICKERS = ['fut_us_gc', 'fut_us_pl', 'fut_us_pa', 'idx_us_ndx', 'idx_us_gspc', 'idx_us_us30']
    AIRFLOW_MAX_TASKS_IN_TASK_MAPPING = 10
    SRAVZ_DATA_MUTUAL_FUNDS_FUNDAMENTALS_PREFIX = f'mutual_funds/fundamentals/'
    # RSS Feed URLs
    FEEDS_COLLECTION = 'rss_feeds'
    FEEDS_TO_PROCESS_WITH_LAST_MINS = 30
    FEED_URLS = {
        "cnbc_top_news":                  "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "cnbc_world_news":                "https://www.cnbc.com/id/100727362/device/rss/rss.html",
        "cnbc_asia_news":                 "https://www.cnbc.com/id/15837362/device/rss/rss.html",
        "cnbc_europe_news":               "https://www.cnbc.com/id/19794221/device/rss/rss.html",
        "cnbc_business_news":             "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "cnbc_earnings_news":             "https://www.cnbc.com/id/15839135/device/rss/rss.html",
        "cnbc_commentary":                "https://www.cnbc.com/id/100370673/device/rss/rss.html",
        "cnbc_economy":                   "https://www.cnbc.com/id/20910258/device/rss/rss.html",
        "cnbc_finance":                   "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "cnbc_technology":                "https://www.cnbc.com/id/19854910/device/rss/rss.html",
        "cnbc_politics":                  "https://www.cnbc.com/id/10000113/device/rss/rss.html",
        "cnbc_health_care":               "https://www.cnbc.com/id/10000108/device/rss/rss.html",
        "cnbc_real_estate":               "https://www.cnbc.com/id/10000115/device/rss/rss.html",
        "cnbc_wealth":                    "https://www.cnbc.com/id/10001054/device/rss/rss.html",
        "cnbc_autos":                     "https://www.cnbc.com/id/10000101/device/rss/rss.html",
        "cnbc_energy":                    "https://www.cnbc.com/id/19836768/device/rss/rss.html",
        "cnbc_media":                     "https://www.cnbc.com/id/10000110/device/rss/rss.html",
        "cnbc_retail":                    "https://www.cnbc.com/id/10000116/device/rss/rss.html",
        "cnbc_travel":                    "https://www.cnbc.com/id/10000739/device/rss/rss.html",
        "cnbc_small_business":            "https://www.cnbc.com/id/44877279/device/rss/rss.html",
        "kitco":                          "http://news.kitco.com/rss/",
        "wsj_opinion":                    "https://feeds.a.dj.com/rss/RSSOpinion.xml",
        "wsj_world_news":                 "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
        "wsj_us_business_news":           "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
        "wsj_market_news":                "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "wsj_technology":                 "https://feeds.a.dj.com/rss/RSSWSJD.xml",
        "wsj_life_style":                 "https://feeds.a.dj.com/rss/RSSLifestyle.xml",
        "yahoo_finance":                  "https://finance.yahoo.com/news/rssindex",
        "ibitimes":                        "https://www.ibtimes.sg/rss/economy",
        "south_china_biz" : "https://www.scmp.com/rss/92/feed",
        "south_china_companies": "https://www.scmp.com/rss/10/feed",
        "south_china_properties": "https://www.scmp.com/rss/96/feed",
        "south_china_world": "https://www.scmp.com/rss/12/feed",
        "south_china_money_wealth": "https://www.scmp.com/rss/318200/feed",
        "japanese_times": "https://www.japantimes.co.jp/news_category/business/feed/",
        "australian_business" : "http://www.businessnews.com.au/rssfeed/latest.rss"
	}

    ### IBKR Settings
    IBKR_API_HOSTNAME="ibkr"
    IBKR_API_PORT=8888
    IBKR_API_CLIEND_ID=1008
    IBKR_SCANNER_PARAMS_XML_FILE_PATH="/tmp/params.xml"
    IBKR_SCANNER_PARAMS_JSON_FILE_PATH="/tmp/params.json"

    ###
    EOD_URL = "https://eodhistoricaldata.com"
    EOD_ETF_LIST_URL = f"{EOD_URL}/download/List_Of_Supported_ETFs.csv"

    ##
    MUTUAL_FUNDS_FUNDAMENTAL_DATA_DAYS_BEFORE_UPDATE = 30