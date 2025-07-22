import os, matplotlib
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
from src.util import settings, helper, logger, aws_cache
from src.services import price_queries
from src.services.cache import Cache
from src.services import mdb
from src.services import aws
from src.analytics import pca
import json, datetime, hashlib
import pandas as pd
import uuid
import matplotlib.pyplot as plt
from . import tears, stocker_tears
from dateutil.relativedelta import relativedelta

class engine(object):

    def __init__(self):
        self.aws_engine = aws.engine()
        self.weekly = 5
        self.monthly = 22
        self.yearly = 255
        self.pqe = price_queries.engine()
        self.pcae = pca.engine()
        self.aws_cache_engine = aws_cache.engine()
        self.logger = logger.RotatingLogger(__name__).getLogger()

    """Performs statistical operations on the df"""
    def upload_stats_to_aws(self, bucket_name, key_name, data,
                            expires = settings.constants.DEFAULT_BUCKET_KEY_EXPIRY):
        self.aws_engine.upload_if_object_not_found(bucket_name,
                                                   key_name, data)

    def handle_cache_aws(self, cache_key, bucket_name, aws_key, data_function, upload_to_aws, orient='split'):
        value = Cache.Instance().get(cache_key)
        if not (isinstance(value, pd.core.frame.DataFrame) or value):
            value = data_function()
            Cache.Instance().add(cache_key, value)
        if upload_to_aws:
            if isinstance(value, pd.core.frame.DataFrame):
                value = value.to_json(date_format='iso', orient=orient).replace("T00:00:00.000Z", "")
            self.upload_stats_to_aws(bucket_name, aws_key, json.dumps(value, cls=helper.DatesEncoder))
        return { 'bucket_name': bucket_name,
                 'key_name': aws_key,
                 'data': value,
                 'signed_url': self.aws_engine.get_signed_url(bucket_name, aws_key)}

    def get_risk_stats(self, sravzid, start_date = None, end_date = None,
                       number_of_years_back = 10,
                       positions = None,
                       transactions = None,
                       upload_to_aws = False, stat = 'risk_stats'):
        '''
            # Get risk stats for given sravzid
            from src.analytics import risk
            reng = risk.engine()
            reng.get_risk_stats("stk_us_FB")
        '''
        sravz_id_hash = hashlib.md5(json.dumps(sravzid, sort_keys=True)).hexdigest()
        cache_key = 'get_risk_stats_%s_%s_%s'%(sravz_id_hash, stat, number_of_years_back)
        aws_key = "get_risk_stats_%s_by_timeframe_%s_%s"%(stat, sravz_id_hash, number_of_years_back)
        bucket_name = settings.constants.risk_stats_bucket_name
        def data_function():
            benchmark_rets = utils.get_symbol_rets('SPY')
            estimate_intraday = 'infer'
            sdate = start_date or datetime.datetime.now() - datetime.timedelta(days=number_of_years_back*365)
            edate = end_date or datetime.datetime.now()
            returns = pf.utils.get_symbol_rets(settings.constants.get_stock_ticker_from_sravz_id(sravzid),
                                               start = sdate,
                                               end = edate)
            stats = timeseries.perf_stats_bootstrap(returns, benchmark_rets)
            return stats
        return self.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws, orient = 'table')

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_returns_tear_sheet(self, sravzid, index = 'idx_us_gspc', start_date = None, end_date = None,
                       number_of_years_back = 10,
                       positions = None,
                       transactions = None,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Get risk stats for given sravzid
            from src.analytics import risk
            reng = risk.engine()
            reng.get_risk_stats("stk_us_FB")
        '''

        try:
            stock_rets = self.pcae.get_percent_daily_returns([sravzid]).tz_localize(None)
            benchmark_rets = self.pcae.get_percent_daily_returns([index]).tz_localize(None)
            if number_of_years_back:
                stock_rets = stock_rets[stock_rets.index > (datetime.datetime.now() - relativedelta(years=number_of_years_back))]
                benchmark_rets = benchmark_rets[benchmark_rets.index > datetime.datetime.now() - relativedelta(years=number_of_years_back)]

            return tears.create_returns_tear_sheet(stock_rets.squeeze(), benchmark_rets=benchmark_rets.squeeze(),
            return_fig = True, sravzid = sravzid)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None

    def get_bayesian_tear_sheet(self, sravzid, index = 'idx_us_gspc', start_date = None, end_date = None,
                       number_of_years_back = 10,
                       out_of_sample_index = -40,
                       positions = None,
                       transactions = None,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns bayesian analysis
        '''
        sravz_id_hash = hashlib.md5(sravzid.encode()).hexdigest()
        cache_key = 'get_bayesian_tear_sheet%s_%s'%(sravz_id_hash, number_of_years_back)
        aws_key = "get_bayesian_tear_sheet%s_by_timeframe_%s"%(sravz_id_hash, number_of_years_back)
        bucket_name = settings.constants.risk_stats_bucket_name
        def data_function():
            data_files = {}
            try:
                stock_rets = self.pcae.get_percent_daily_returns([sravzid]).tz_localize('UTC', level=0)
                # Fails with benchmark_rets
                # benchmark_rets = self.pcae.get_percent_daily_returns([index]).tz_localize('UTC', level=0)
                if len(stock_rets) > -out_of_sample_index:
                    out_of_sample = stock_rets.index[out_of_sample_index]
                else:
                    out_of_sample = stock_rets.index[len(stock_rets)* 1/9]
                fig = tears.create_bayesian_tear_sheet(stock_rets.squeeze(), return_fig=True,live_start_date=out_of_sample)
                file_path = helper.util.get_temp_file()
                fig.savefig(file_path)
                plt.close(fig)
                data_files['bayesian_tear_sheet'] = "{0}.png".format(file_path)
            except Exception:
                self.logger.error("Error plotting bayesian_tear_sheet for: %s" % (sravzid), exc_info=True)
                data_files['bayesian_tear_sheet'] = None
            return data_files
        return self.aws_cache_engine.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    def get_stocker_tear_sheet(self, sravzid, chart_type, number_of_years_back = 10):
        '''
            # Returns stocker analysis
        '''
        try:
            return stocker_tears.create_stocker_tear_sheet(sravzid, chart_type, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_predict_future(self, sravzid, start_date = None, end_date = None,
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        try:
            return self.get_stocker_tear_sheet(sravzid, stocker_tears.CHART_TYPE_PREDICT_FUTURE, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_prophet_model(self, sravzid, start_date = None, end_date = None,
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        try:
            return self.get_stocker_tear_sheet(sravzid, stocker_tears.CHART_TYPE_CREATE_PROPHET_MODEL, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_evaluate_prediction(self, sravzid, start_date = None, end_date = None,
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        try:
            return self.get_stocker_tear_sheet(sravzid, stocker_tears.CHART_TYPE_EVALUATE_PREDICTION, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_change_point_prior_analysis(self, sravzid, start_date = None, end_date = None,
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        try:
            return self.get_stocker_tear_sheet(sravzid, stocker_tears.CHART_TYPE_CHANGE_POINT_PRIOR_ANALYSIS, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_change_point_prior_validation(self, sravzid, start_date = None, end_date = None,
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        try:
            return self.get_stocker_tear_sheet(sravzid, stocker_tears.CHART_TYPE_CHANGE_POINT_PRIOR_VALIDATION, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_prediciton_with_change_point(self, sravzid, start_date = None, end_date = None,
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        try:
            return self.get_stocker_tear_sheet(sravzid, stocker_tears.CHART_TYPE_EVALUATE_PREDICTION_WITH_CHANGE_POINT, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for: %s" % (sravzid), exc_info=True)
            return None
