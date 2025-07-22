import collections
import json
import datetime
import io
import hashlib
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from src.util import settings, helper, logger, aws_cache
from src.services import price_queries
from src.services.cache import Cache
from src.services import mdb
from src.services import aws
from src.util import plot
from . import tears


class engine(object):
    """Performs statistical operations on the df"""

    def __init__(self):
        self.aws_engine = aws.engine()
        self.weekly = 5
        self.monthly = 22
        self.yearly = 255
        self.pqe = price_queries.engine()
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.aws_cache_engine = aws_cache.engine()

    def getting_rolling_stats(self, df):
        weeklyrollmean = df.rolling(window=5).mean().sort_index()
        weeklyrollstd = df.rolling(window=5).std().sort_index()
        monthlyrollmean = df.rolling(window=22).mean().sort_index()
        monthlyrollstd = df.rolling(window=22).std().sort_index()
        yearlyrollmean = df.rolling(window=255).mean().sort_index()
        yearlyrollstd = df.rolling(window=255).std().sort_index()
        return {
            'weeklyrollmean': weeklyrollmean,
            'weeklyrollstd': weeklyrollstd,
            'monthlyrollmean': monthlyrollmean,
            'monthlyrollstd': monthlyrollstd,
            'yearlyrollmean': yearlyrollmean,
            'yearlyrollstd': yearlyrollstd
        }

    def getting_rolling_stat_by_timeframe(self, df, stat, time_frame):
        '''
            stat = mean|std
            time_frame
                         self.weekly = 5
                         self.monthly = 22
                         self.yearly = 255

            se = engine()
            pqe = price_queries.engine()
            se.getting_rolling_stat_by_timeframe(pqe.get_historical_price_df('fut_gold_feb_17_usd_lme'), 'mean', se.weekly)
        '''

        if stat == 'mean':
            data_df = df.rolling(window=time_frame).mean().sort_index()
        elif stat == 'std':
            data_df = df.rolling(window=time_frame).std().sort_index()
        data_df = data_df.round(2)
        data_df = data_df.reset_index()

        return {
            'columns': data_df.columns.tolist(),
            'values': data_df.values.tolist(),
        }

    def perform_df_test(self, series):
        # Performs dickey fuller test
        series = series.dropna()
        dftest = adfuller(series, autolag='AIC')
        dfoutput = pd.Series(dftest[0:4], index=[
                             'Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
        for key, value in list(dftest[4].items()):
            dfoutput['Critical Value (%s)' % key] = value
        return json.loads(dfoutput.to_json(date_format='iso').replace('T00:00:00.000Z', ''))

    def get_key_name_from_sravz_id(self, sravzid, algorithm='historical_rolling_stats'):
        if algorithm == 'historical_rolling_stats':
            return "%s_%s" % (helper.get_generic_sravz_id(sravzid), algorithm)
        return None

    def get_historical_rolling_stats_by_timeframe(self, sravzid, stat, time_frame, upload_to_aws=False):
        '''
            bucket_name: sravz-historical-rolling-stats
            stat = mean|std
            time_frame
                         self.weekly = 5
                         self.monthly = 22
                         self.yearly = 255
            se = engine()
            se.get_historical_rolling_stats_by_timeframe('fut_gold_feb_17_usd_lme', 'mean', se.weekly)
            se.get_historical_rolling_stats_by_timeframe('fut_gold_feb_17_usd_lme', 'mean', se.weekly, upload_to_aws = True)
        '''
        sravz_generic_id = helper.get_generic_sravz_id(sravzid)
        cache_key = 'get_historical_rolling_stats_%s_%s_%s' % (
            sravz_generic_id, stat, time_frame)
        aws_key = "historical_rolling_%s_by_timeframe_%s_%s" % (
            stat, sravz_generic_id, time_frame)
        bucket_name = settings.constants.historical_rolling_stats_bucket_name

        def data_function():
            data_df = self.pqe.get_historical_price_df(sravzid)
            rolling_stats_df = self.getting_rolling_stat_by_timeframe(
                data_df, stat, time_frame)
            return {"%s_%s" % (stat, time_frame): rolling_stats_df}
        return self.aws_engine.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    def get_rolling_stats_by_sravz_id(self, sravz_id, upload_to_aws=False):
        '''
            from src.analytics import stats
            stats_engine = stats.engine()
            stats_engine.get_rolling_stats_by_sravz_id('fut_us_gc')        
        '''
        sravz_generic_id = helper.get_generic_sravz_id(sravz_id)
        cache_key = 'get_rolling_stats_by_sravz_id_%s' % (sravz_generic_id)
        bucket_name = settings.constants.historical_rolling_stats_bucket_name
        from_date = (datetime.datetime.now() - datetime.timedelta(
            days=settings.constants.number_of_years*365)).strftime("%Y-%m-%d")

        def data_function():
            data_df = self.pqe.get_historical_price_df(sravz_id)[from_date:]
            stats_df = self.getting_rolling_stats(data_df)
            for k, v in stats_df.items():
                plot.util.save_df_plot(plot.util.plot_df(v.cumsum()), "{0}_{1}_{2}".format(
                    "get_rolling_stats_by_sravz_id", sravz_id, k))
            return stats_df
        return self.aws_engine.handle_cache_aws(cache_key, bucket_name, cache_key, data_function, upload_to_aws)

    def check_rolling_stats_alert_triggered(self, sravz_id):
        '''
            from src.analytics import stats
            stats_engine = stats.engine()
            stats_engine.check_rolling_stats_alert_triggered('fut_us_gc')
        '''
        price_df = self.pqe.get_historical_price_df(sravz_id)
        stats_df = self.getting_rolling_stats(price_df)
        return [{'Statistic' : key,
            'AdjustedClose' : stats_df[key].iloc[[-1]]['AdjustedClose'].values[0],
            'CurrentAdjustedClose'  : price_df.iloc[[-1]]['AdjustedClose'].values[0],
            'AlertTriggered' : stats_df[key].iloc[[-1]]['AdjustedClose'].values[0] > price_df.iloc[[-1]]['AdjustedClose'].values[0]
            } for key in stats_df.keys() if 'mean' in key]

    def get_rolling_stats_by_sravz_id_timeframe(self, sravz_id, stat_by, timeframe, upload_to_aws=False):
        '''
        '''
        sravz_generic_id = helper.get_generic_sravz_id(sravz_id)
        cache_key = 'get_rolling_stats_by_sravz_id_timeframe_{0}_{1}_{2}'.format(
            sravz_generic_id, stat_by, timeframe)
        bucket_name = settings.constants.historical_rolling_stats_bucket_name
        from_date = (datetime.datetime.now() - datetime.timedelta(
            days=settings.constants.number_of_years*365)).strftime("%Y-%m-%d")

        def data_function():
            data_df = self.pqe.get_historical_price_df(sravz_id)[from_date:]
            stats_df = None
            if stat_by == 'mean':
                stats_df = data_df.rolling(
                    window=timeframe).mean().sort_index()
            elif stat_by == 'std':
                stats_df = data_df.rolling(window=timeframe).std().sort_index()
            return stats_df
        return self.aws_engine.handle_cache_aws(cache_key, bucket_name, cache_key, data_function, upload_to_aws)

    def get_df_test_by_sravz_id(self, sravz_id, upload_to_aws=False):
        '''
        '''
        sravz_generic_id = helper.get_generic_sravz_id(sravz_id)
        cache_key = 'get_df_test_by_sravz_id_%s' % (sravz_generic_id)
        bucket_name = settings.constants.historical_rolling_stats_bucket_name
        from_date = (datetime.datetime.now() - datetime.timedelta(
            days=settings.constants.number_of_years*365)).strftime("%Y-%m-%d")

        def data_function():
            data_df = self.pqe.get_historical_price_df(sravz_id)[from_date:]
            ticker_type = helper.get_ticker_type(sravz_id)
            column_to_use = None
            if ticker_type == settings.constants.TICKER_TYPE_FUTURE:
                column_to_use = 'Settle'
            elif ticker_type == settings.constants.TICKER_TYPE_STOCK:
                column_to_use = 'Last'
            else:
                raise ValueError(
                    'Invalid ticker type for Sravz ID {0}'.format(sravz_id))
            stats_df_test = self.perform_df_test(data_df[column_to_use])
            return stats_df_test
        return self.aws_engine.handle_cache_aws(cache_key, bucket_name, cache_key, data_function, upload_to_aws)

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_rollingstats_tear_sheet(self, sravzid, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_PC):
        '''
            # Get risk stats for given sravzid
            from src.analytics import risk
            reng = risk.engine()
            reng.get_risk_stats("stk_us_FB")
        '''
        try:
            return tears.get_rolling_stats(sravzid)
        except Exception:
            logger.logging.exception(
                'Error plotting get_rollingstats_tear_sheet')
            return None
        return None

################### Kafka callable functions ####################

    def get_df_stats_by_sravz_id(self, sravz_id, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_PC):
        '''
            # Get price data frame stats
        '''
        sravz_generic_id = helper.get_generic_sravz_id(sravz_id)
        cache_key = 'get_df_stats_by_sravz_id_%s' % (sravz_generic_id)
        bucket_name = settings.constants.AWS_PRICE_DF_STATS
        from_date = (datetime.datetime.now() - datetime.timedelta(
            days=settings.constants.number_of_years*365)).strftime("%Y-%m-%d")

        def data_function():
            if helper.is_user_asset(sravz_id):
                data_df = pd.read_csv(
                    io.BytesIO(aws.engine().download_object(settings.constants.AWS_USER_ASSETS_BUCKET, sravz_id).decode(
                        'utf-8').replace("\r\n", "\n").encode('utf-8'))
                )
            else:
                data_df = self.pqe.get_historical_price_df(sravz_id)[
                    from_date:]
            df_describe = data_df.describe()
            return df_describe
        return self.aws_engine.handle_cache_aws(cache_key, bucket_name, cache_key, data_function, upload_to_aws)

    def get_dickey_fuller_stats(self, sravzid, upload_to_aws=False):
        '''
            se = engine()
            se.get_dickey_fuller_stats('fut_gold_feb_17_usd_lme')
            se.get_dickey_fuller_stats('fut_gold_feb_17_usd_lme', upload_to_aws = True)
            se.get_dickey_fuller_stats('fut_oil_feb_17_usd_lme', upload_to_aws = True)

            Returns:
            { 'bucket_name': bucket_name, 'key_name': aws_key, 'data': value}
        '''
        sravz_generic_id = helper.get_generic_sravz_id(sravzid)
        cache_key = 'get_dickey_fuller_stats_%s' % (sravz_generic_id)
        aws_key = "dickey_fuller_stats_%s" % (
            helper.get_generic_sravz_id(sravzid))
        bucket_name = settings.constants.historical_rolling_stats_bucket_name

        def data_function():
            data_df_all = self.pqe.get_historical_price_df(sravzid)
            value = {'df_test_all': self.perform_df_test(data_df_all)}
            for days in [self.monthly, self.yearly]:
                value.update({'df_test_%sdays' % (days): self.perform_df_test(
                    data_df_all[helper.util.get_n_days_back_date(days):])})
            for years in [3, 5, 10, 15, 20, 25, 30]:
                value.update({'df_test_%syear' % (years): self.perform_df_test(
                    data_df_all[helper.util.get_n_years_back_date(years):])})
            return value
        return self.aws_engine.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    def get_historical_rolling_stats_by_week(self, sravzid, stat, upload_to_aws=False):
        '''
            se = engine()
            se.get_historical_rolling_stats_by_week('fut_gold_feb_17_usd_lme', 'mean')
            se.get_historical_rolling_stats_by_week('fut_gold_feb_17_usd_lme', 'std')
            se.get_historical_rolling_stats_by_week('fut_gold_feb_17_usd_lme', 'mean', upload_to_aws = True)
            se.get_historical_rolling_stats_by_week('fut_gold_feb_17_usd_lme', 'std', upload_to_aws = True)

            Returns:
            { 'bucket_name': bucket_name, 'key_name': aws_key, 'data': value}
        '''
        return self.get_historical_rolling_stats_by_timeframe(sravzid, stat, self.weekly, upload_to_aws)

    def get_historical_rolling_stats_by_month(self, sravzid, stat, upload_to_aws=False):
        '''
            se = engine()
            se.get_historical_rolling_stats_by_month('fut_gold_feb_17_usd_lme', 'mean')
            se.get_historical_rolling_stats_by_month('fut_gold_feb_17_usd_lme', 'std')
            se.get_historical_rolling_stats_by_month('fut_gold_feb_17_usd_lme', 'mean', upload_to_aws = True)
            se.get_historical_rolling_stats_by_month('fut_gold_feb_17_usd_lme', 'std', upload_to_aws = True)

            Returns:
            { 'bucket_name': bucket_name, 'key_name': aws_key, 'data': value}
        '''
        return self.get_historical_rolling_stats_by_timeframe(sravzid, stat, self.monthly, upload_to_aws)

    def get_historical_rolling_stats_by_year(self, sravzid, stat, upload_to_aws=False):
        '''
            se = engine()
            se.get_historical_rolling_stats_by_year('fut_gold_feb_17_usd_lme', 'mean')
            se.get_historical_rolling_stats_by_year('fut_gold_feb_17_usd_lme', 'std')
            se.get_historical_rolling_stats_by_year('fut_gold_feb_17_usd_lme', 'mean', upload_to_aws = True)
            se.get_historical_rolling_stats_by_year('fut_gold_feb_17_usd_lme', 'std', upload_to_aws = True)
            se.get_historical_rolling_stats_by_year('fut_oil_feb_17_usd_lme', 'std', upload_to_aws = True)

            Returns:
            { 'bucket_name': bucket_name, 'key_name': aws_key, 'data': value}
        '''
        return self.get_historical_rolling_stats_by_timeframe(sravzid, stat, self.yearly, upload_to_aws)
