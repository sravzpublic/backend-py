from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.util import aws_cache, settings, helper, logger
from src.services import price_queries
from src.services.cache import Cache
from src.services import mdb
from src.services import aws
from sklearn.decomposition import PCA
from scipy import stats
import collections
import json
import datetime
import hashlib
import uuid
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from src.analytics import tears, util
#plt.ioff()


class engine(object):

    def __init__(self):
        self.aws_engine = aws.engine()
        self.weekly = 5
        self.monthly = 22
        self.yearly = 255
        self.pqe = price_queries.engine()
        self.aws_cache_engine = aws_cache.engine()
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.util = util.Util()

    """Performs statistical operations on the df"""

    def upload_stats_to_aws(self, bucket_name, key_name, data,
                            expires=settings.constants.DEFAULT_BUCKET_KEY_EXPIRY):
        self.aws_engine.upload_if_object_not_found(bucket_name,
                                                   key_name, data)

    def handle_cache_aws(self, cache_key, bucket_name, aws_key, data_function, upload_to_aws):
        value = Cache.Instance().get(cache_key)
        if not (isinstance(value, pd.core.frame.DataFrame) or value):
            value = data_function()
            Cache.Instance().add(cache_key, value)
        if upload_to_aws:
            if isinstance(value, pd.core.frame.DataFrame):
                value = value.to_json(date_format='iso', orient='split').replace(
                    "T00:00:00.000Z", "")
            self.upload_stats_to_aws(bucket_name, aws_key, json.dumps(
                helper.convert(value), cls=helper.DatesEncoder))
        return {'bucket_name': bucket_name,
                'key_name': aws_key,
                'data': value,
                'signed_url': self.aws_engine.get_signed_url(bucket_name, aws_key)}

    def get_scatter_plot_data(self, sravzids, time_frame_in_years, upload_to_aws=False, stat='pca'):
        '''
            # In years
            time_frame_in_years = 10
            stat = 'pca'
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            from src.analytics import pca
            pcae = pca.engine()
            pcae.get_scatter_plot_data(sravzids, time_frame_in_years)
            # se.get_historical_rolling_stats_by_timeframe('fut_gold_feb_17_usd_lme', 'mean', se.weekly, upload_to_aws = True)
        '''
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravz_id) for sravz_id in sravzids]
        sravz_generic_ids_hash = hashlib.md5(json.dumps(
            sravz_generic_ids, sort_keys=True).encode()).hexdigest()
        cache_key = 'get_scatter_plot_data_%s_%s_%s' % (
            sravz_generic_ids_hash, stat, time_frame_in_years)
        aws_key = "get_scatter_plot_data_%s_by_timeframe_%s_%s" % (
            stat, sravz_generic_ids_hash, time_frame_in_years)
        bucket_name = settings.constants.pca_scatter_plot_bucket_name

        def data_function():
            data_dfs = [self.pqe.get_historical_price_df(
                sravzids).tz_localize(None) for sravzids in sravz_generic_ids]
            data_dfs = [data_df[data_df.index > datetime.datetime.now(
            ) - relativedelta(years=time_frame_in_years)] for data_df in data_dfs]
            return data_dfs
        return self.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    def get_price_data_dfs(self, sravzids, time_frame_in_years=10):
        '''
            Returns percent daily returns
            from src.analytics import pca
            pcae = pca.engine()
            pcae.get_percent_daily_returns()
        '''
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravz_id) for sravz_id in sravzids]
        data_dfs = []
        data_df = None
        for sravzid in sravz_generic_ids:
            try:
                data_df = self.pqe.get_historical_price_df(sravzid)
                data_dfs.append(data_df)
            except Exception:
                self.logger.error('Failed to process sravz_id %s' %
                                  (sravzid), exc_info=True)
        if data_dfs:
            data_dfs = [data_df[data_df.index > datetime.datetime.now(
            ) - relativedelta(years=time_frame_in_years)] for data_df in data_dfs]
            data_df = pd.concat(data_dfs, axis=1)
        return data_df

    def get_percent_daily_returns(self, sravzids, time_frame_in_years=10, src='aws'):
        '''
            Returns percent daily returns
            from src.analytics import pca
            pcae = pca.engine()
            pcae.get_percent_daily_returns()
        '''
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravz_id) for sravz_id in sravzids]
        data_dfs = []
        data_df = None
        for sravzid in sravz_generic_ids:
            try:
                data_df = self.pqe.get_historical_price_df(sravzid, src=src)
                col_to_use = helper.get_price_column_to_use_for_the_asset(sravzid, data_df, change_cols_to_titlecase=False)
                data_df.fillna(method="ffill", inplace=True)
                data_df = data_df[[col_to_use]].pct_change(periods=1).rename(columns={col_to_use: '{0}_{1}_pct_chg'.format(sravzid, col_to_use)})
                data_dfs.append(data_df)
            except Exception:
                self.logger.error('Failed to process sravz_id %s' %
                                  (sravzid), exc_info=True)
        if data_dfs:
            data_dfs = [data_df[data_df.index > datetime.datetime.now(
            ) - relativedelta(years=time_frame_in_years)] for data_df in data_dfs]
            data_df = pd.concat(data_dfs, axis=1)
        return data_df

    def get_scatter_plot_daily_return(self, sravzids, time_frame_in_years=10, upload_to_aws=False, stat='pca', device=settings.constants.DEVICE_TYPE_PC):
        '''
            # In years
            time_frame_in_years = 10
            stat = 'pca'
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            from src.analytics import pca
            pcae = pca.engine()
            sravzids = ["stk_us_ayi", "stk_us_axp", "stk_us_awk",
                "stk_us_azo", "stk_us_avb", "stk_us_avy", "stk_us_avg"]
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            pcae.get_scatter_plot_daily_return(sravzids, time_frame_in_years)
            pcae.get_scatter_plot_daily_return(
                sravzids, time_frame_in_years, upload_to_aws = True)
            # se.get_historical_rolling_stats_by_timeframe('fut_gold_feb_17_usd_lme', 'mean', se.weekly, upload_to_aws = True)
        '''
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravz_id) for sravz_id in sravzids]
        sravz_generic_ids_hash = hashlib.md5(json.dumps(
            sravz_generic_ids, sort_keys=True).encode()).hexdigest()
        cache_key = 'get_scatter_plot_daily_return_%s_%s_%s' % (
            sravz_generic_ids_hash, stat, time_frame_in_years)
        aws_key = "get_scatter_plot_daily_return_%s_by_timeframe_%s_%s" % (
            stat, sravz_generic_ids_hash, time_frame_in_years)
        bucket_name = settings.constants.pca_scatter_plot_bucket_name

        def data_function():
            data_df = self.get_percent_daily_returns(
                sravzids, time_frame_in_years=time_frame_in_years)
            if device == settings.constants.DEVICE_TYPE_MOBILE:
                fig = plt.figure()
                plt.close(fig)
                data_files = {}
                if not data_df.empty:
                    try:
                        data_df.plot()
                        file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
                        plt.savefig(file_path)
                        data_files['scatter_plot'] = "{0}.png".format(
                            file_path)
                    except Exception:
                        self.logger.exception('Error plotting scatter plot')
                        data_files['scatter_plot'] = None
                    return data_files
                return None
            else:
                return data_df
        return self.aws_cache_engine.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    def get_pca_components(self, sravzids, n_components=2, time_frame_in_years=10,
                           upload_to_aws=False, stat='pca', index='idx_us_gspc',
                           device=settings.constants.DEVICE_TYPE_PC):
        '''
            # In years
            n_components = 2
            stat = 'pca'
            from src.analytics import pca
            pcae = pca.engine()
            sravzids = ["stk_us_ayi", "stk_us_axp", "stk_us_awk",
                "stk_us_azo", "stk_us_avb", "stk_us_avy", "stk_us_avg"]
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            pcae.get_pca_components(sravzids, n_components)
            pcae.get_pca_components(
                sravzids, n_components, upload_to_aws = True)
        '''
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravz_id) for sravz_id in sravzids]
        sravz_generic_ids_hash = hashlib.md5(json.dumps(
            sravz_generic_ids, sort_keys=True).encode()).hexdigest()
        cache_key = 'get_pca_components_%s_%s_%s' % (
            sravz_generic_ids_hash, stat, n_components)
        aws_key = 'get_pca_components_%s_%s_%s' % (
            stat, sravz_generic_ids_hash, n_components)
        bucket_name = settings.constants.pca_components_bucket_name

        def data_function():
            data = self.get_scatter_plot_daily_return(sravzids,
                                                      time_frame_in_years=time_frame_in_years,
                                                      upload_to_aws=False,
                                                      stat=stat)
            _data = data.replace([np.inf, -np.inf], np.nan).fillna(0)
            _p = PCA(n_components=n_components)
            pca_dat = _p.fit(_data)
            fig = plt.figure()
            plt.close(fig)
            plt.bar(range(n_components), pca_dat.explained_variance_ratio_)
            plt.title(
                'Variance explained by first {0} principal components'.format(n_components))
            file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
            plt.savefig(file_path)
            return {
                # 'n_components': n_components,
                # 'explained_variance': pca_dat.explained_variance_ratio_.tolist(),
                # 'pca_components':  pca_dat.components_.tolist(),
                # 'transformed_data_first_pc': transformed_data_first_pc,
                # 'transformed_data_second_pc': transformed_data_second_pc,
                # 'raw_data': _data.to_json(date_format='iso').replace("T00:00:00.000Z", ""),
                'explained_variance_fig': "{0}.png".format(file_path)
            }
        return self.aws_cache_engine.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    def get_pca_components_vs_index_returns(self, sravzids, n_components=2, time_frame_in_years=10,
                                            upload_to_aws=False, stat='pca', index=settings.constants.BENCHMARK_INDEX,
                                            device=settings.constants.DEVICE_TYPE_PC):
        '''
            # In years
            n_components = 2
            stat = 'pca'
            from src.analytics import pca
            pcae = pca.engine()
            sravzids = ["stk_us_ayi", "stk_us_axp", "stk_us_awk",
                "stk_us_azo", "stk_us_avb", "stk_us_avy", "stk_us_avg"]
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            pcae.get_pca_components(sravzids, n_components)
            pcae.get_pca_components(
                sravzids, n_components, upload_to_aws = True)
        '''
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravz_id) for sravz_id in sravzids]
        sravz_generic_ids_hash = hashlib.md5(json.dumps(
            sravz_generic_ids, sort_keys=True).encode()).hexdigest()
        cache_key = 'get_pca_components_vs_index_returns_%s_%s_%s' % (
            sravz_generic_ids_hash, stat, n_components)
        aws_key = 'get_pca_components_vs_index_returns_%s_%s_%s' % (
            stat, sravz_generic_ids_hash, n_components)
        bucket_name = settings.constants.pca_components_bucket_name
        index_column = settings.constants.BENCHMARK_INDEX_COLUMN

        def data_function():
            data = self.get_scatter_plot_daily_return(sravzids,
                                                      time_frame_in_years=time_frame_in_years,
                                                      upload_to_aws=False,
                                                      stat=stat)
            _data = data.replace([np.inf, -np.inf], np.nan).fillna(0)
            _p = PCA(n_components=n_components)
            pca_dat = _p.fit(_data)
            first_pc = pca_dat.components_[0]
            # # plot data
            fig = plt.figure()
            plt.close(fig)
            # https://thequantmba.wordpress.com/2017/01/24/principal-component-analysis-of-equity-returns-in-python/
            # normalized to 1
            first_pc_normalized_to_1 = np.asmatrix(first_pc/sum(first_pc)).T
            # apply our first componenet as weight of the stocks
            first_pc_portfolio_return = _data.values*first_pc_normalized_to_1
            # plot the total return index of the first PC portfolio
            pc_ret = pd.DataFrame(
                data=first_pc_portfolio_return, index=_data.index)
            pc_ret_idx = pc_ret+1
            pc_ret_idx = pc_ret_idx.cumprod()
            pc_ret_idx.columns = ['pc1']
            # index_retruns_df = self.get_percent_daily_returns([index], time_frame_in_years = time_frame_in_years)
            index_retruns_df = self.pqe.get_historical_price_df(index)[
                [index_column]]
            # pc_ret_idx['indu'] = data_index['fut_spx_last_pct_chg']
            pc_ret_vs_idx_returns = pc_ret_idx.join(index_retruns_df)
            pc_ret_vs_idx_returns.plot(subplots=True, title='First PC Portfolio vs {0} {1} Price'.format(
                index, index_column), layout=[1, 2])
            file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
            plt.savefig(file_path)
            return {
                'pc_returns_vs_index_returns_fig': "{0}.png".format(file_path)
            }
        return self.aws_cache_engine.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    def get_covariance_matrix(self, sravzids, time_frame_in_years=10, upload_to_aws=False, stat='pca', device=settings.constants.DEVICE_TYPE_PC):
        '''
            # In years
            stat = 'pca'
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            pcae.get_covariance_matrix(sravzids)
            pcae.get_covariance_matrix(
                sravzids, n_components, upload_to_aws = True)
        '''
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravz_id) for sravz_id in sravzids]
        sravz_generic_ids_hash = hashlib.md5(json.dumps(
            sravz_generic_ids, sort_keys=True).encode()).hexdigest()
        cache_key = 'get_covariance_matrix_%s_%s' % (
            sravz_generic_ids_hash, stat)
        aws_key = 'get_covariance_matrix_%s_%s' % (
            stat, sravz_generic_ids_hash)
        bucket_name = settings.constants.pca_covariance_matrix_bucket_name

        def data_function():
            data = self.get_scatter_plot_daily_return(sravzids,
                                                      time_frame_in_years=time_frame_in_years,
                                                      upload_to_aws=False,
                                                      stat=stat)
            _data = data.replace([np.inf, -np.inf], np.nan).fillna(0)
            return {
                'covarince_matrix_html': _data.cov().to_html()
            }
        return self.handle_cache_aws(cache_key, bucket_name, aws_key, data_function, upload_to_aws)

    @aws_cache.save_file_to_s3
    def create_portfolio_pca_report(self, name, user_id, time_frame_in_years=10, upload_to_aws=False, stat='pca', device=settings.constants.DEVICE_TYPE_MOBILE):
        '''
            # In years
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            pcae.get_portfolio_pca(sravzids)
        '''
        portfolio_assets = self.util.get_portfolio_assets(name, user_id)
        data_df = self.get_percent_daily_returns(portfolio_assets,
            time_frame_in_years=time_frame_in_years)
        if device == settings.constants.DEVICE_TYPE_MOBILE:
            if not data_df.empty:
                try:
                    fig = tears.create_portfolio_pca_report(portfolio_assets, return_fig = True)
                    file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
                    self.logger.info(
                        'Portfolio PCA report created: {0}'.format(file_path))
                    fig.savefig(file_path)
                    plt.close(fig)
                    return "{0}.png".format(file_path)
                except Exception:
                    self.logger.exception(
                        'Error plotting portfolio pca')
            return None
        else:
            return data_df


if __name__ == '__main__':
    e = engine()
    df = e.get_price_data_dfs(['idx_us_us10y', 'idx_us_us5y'])
    print(df)
