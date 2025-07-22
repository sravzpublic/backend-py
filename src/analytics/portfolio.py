#!/usr/bin/env python
import datetime
from src.services import mdb, price_queries
from src.util import logger, settings, helper, aws_cache
import uuid
import os, sys
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)
import pca, tears, timeseries
import numpy as np
import matplotlib.pyplot as plt
import tears, stocker_tears, util
from dateutil.relativedelta import relativedelta

class engine(object):
    """Updates portfolio PNL"""

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.mdb_engine = mdb.engine()
        self.pcae_engine = pca.engine()
        self.tse = timeseries.engine()
        self.util = util.Util()

    def get_portfolio_assets_daily_returns(self, name, user_id, portfolio_assets=None):
        '''
            returns portfolio assets daily returns df
        '''
        if not portfolio_assets:
            returns = self.pcae_engine.get_percent_daily_returns(
                self.util.get_portfolio_assets(name, user_id))
        else:
            returns = self.pcae_engine.get_percent_daily_returns(
                portfolio_assets)
        return returns

    def get_portfolio_assets_cummulative_daily_returns(self, name, user_id, portfolio_assets=None):
        '''
            returns portfolio assets daily returns df
        '''
        return ((1+self.get_portfolio_assets_daily_returns(name, user_id, portfolio_assets=portfolio_assets)).cumprod()-1)

    def get_portfolio_daily_returns(self, name, user_id, portfolio_assets=None):
        '''
            returns portfolio daily returns df
        '''
        if not portfolio_assets:
            assets_with_weights = self.util.get_portfolio_assets_weights(name, user_id)
            if assets_with_weights:
                assets = [a[0] for a in assets_with_weights]
                portfolio_weights_ew = [helper.util.getfloat(a[1])/100 for a in assets_with_weights]
                returns = self.pcae_engine.get_percent_daily_returns(assets)
            else:
                self.logger.error("Portfolio Not found: user_id: %s name: %s" % (user_id, name), exc_info=True)
                raise Exception("Portfolio Not found: user_id: %s name: %s" % (user_id, name))
        else:
            # Handle weights from the db
            returns = self.pcae_engine.get_percent_daily_returns(
                portfolio_assets)
            numstocks = len(returns.columns)
            portfolio_weights_ew = np.repeat(1/numstocks, numstocks)

        return returns.iloc[:, 0:len(portfolio_weights_ew)].mul(portfolio_weights_ew, axis=1).sum(axis=1)

    def get_portfolio_cummulative_returns(self, name, user_id, portfolio_assets=None):
        '''
            returns portfolio daily returns df
        '''
        return ((1+self.get_portfolio_daily_returns(name, user_id, portfolio_assets=portfolio_assets)).cumprod()-1)

    def update(self):
        portfolio_collection = self.mdb_engine.get_collection('portfolios')
        portfolioassets_collection = self.mdb_engine.get_collection(
            'portfolioassets')
        portfolio_collection_items = self.mdb_engine.get_collection_items(
            'portfolios', iterator=True)
        quotes_dict = {}
        # Commodities quotes
        futures_quotes = self.mdb_engine.get_collection_items(
            'quotes_commodities', iterator=False, sortBy='pricecapturetime', cache=False)
        [quotes_dict.update({quote["SravzId"].lower(): quote})
         for quote in futures_quotes if quote.get("SravzId").lower()]
        # Stock quotes
        stock_quotes = self.mdb_engine.get_collection_items(
            'quotes_stocks', iterator=False, cache=False)
        [quotes_dict.update({quote["SravzId"].lower(): quote})
         for quote in stock_quotes if quote.get("SravzId").lower()]

        # Get all assets in all portfolios
        # assets = self.mdb_engine.get_collection_items('assets', iterator = False, cache = True)
        # assets_dict = {}
        # assets = helper.convert(assets)
        # [assets_dict.update({str(asset["_id"]): asset["SravzId"]}) for asset in assets]
        for portfolio in portfolio_collection_items:
            try:
                current_portfolio_value = 0
                portfolioAssets = portfolio["portfolioassets"]
                portfolioassets_collection_items = self.mdb_engine.get_collection_items('portfolioassets', find_clause={"_id": {"$in": [id for id
                                                                                                                                        in portfolioAssets]}}, iterator=True)
                for portfolio_asset in portfolioassets_collection_items:
                    # asset_sravz_id = assets_dict.get(str(portfolio_asset["AssetId"]))
                    # if asset_sravz_id:
                    asset_sravz_id = portfolio_asset["SravzId"]
                    asset_quote = quotes_dict.get(
                        helper.get_generic_sravz_id(asset_sravz_id))
                    if not asset_quote:
                        self.logger.warn("Could not get quote for sravz_id %s generic_id %s" % (
                            asset_sravz_id, helper.get_generic_sravz_id(asset_sravz_id)))
                        continue
                    current_asset_price = helper.util.getfloat(helper.util.translate_string_to_number(
                        asset_quote.get("Last"))) * portfolio_asset.get("quantity") * portfolio_asset.get("weight") / 100
                    purchase_asset_price = helper.util.getfloat(helper.util.translate_string_to_number(portfolio_asset.get(
                        "purchaseprice"))) * portfolio_asset.get("quantity") * portfolio_asset.get("weight") / 100
                    # Value == Current Price
                    portfolio_asset["value"] = helper.util.getfloat(helper.util.translate_string_to_number(
                        asset_quote.get("Last")))  # float(asset_quote.get("Last").replace(",",""))
                    portfolio_asset["pnl"] = current_asset_price - \
                        purchase_asset_price
                    portfolio_asset["pnlcalculationdt"] = asset_quote.get(
                        "pricecapturetime")
                    current_portfolio_value = current_asset_price + current_portfolio_value
                    portfolioassets_collection.replace_one(
                        {"_id": portfolio_asset["_id"]}, portfolio_asset)
                    portfolio["value"] = current_portfolio_value
                    portfolio["pnl"] = current_portfolio_value - \
                        portfolio["cost"]
                    portfolio["pnlcalculationdt"] = datetime.datetime.now(datetime.UTC)
                    portfolio_collection.replace_one(
                        {"_id": portfolio["_id"]}, portfolio)
                self.logger.info("Processed portfolio id: %s name: %s PNL" % (
                    portfolio.get("_id"), portfolio.get("name")), exc_info=True)
            except:
                self.logger.error("Could not process portfolio id: %s name: %s" % (
                    portfolio.get("_id"), portfolio.get("name")), exc_info=True)

    @aws_cache.save_file_to_s3
    def create_portfolio_returns_tear_sheet(self, name,  user_id, portfolio_assets=None, time_frame_in_years=10, index='idx_us_gspc', upload_to_aws=False, device=settings.constants.DEVICE_TYPE_MOBILE):
        '''
            # In years
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            pcae.get_portfolio_pca(sravzids)
        '''
        asset_returns = self.get_portfolio_daily_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize(None)
        benchmark_rets = self.pcae_engine.get_percent_daily_returns(
            [index]).tz_localize(None)
        if time_frame_in_years:
            asset_returns = asset_returns[asset_returns.index > datetime.datetime.now() - relativedelta(years=time_frame_in_years)]
            benchmark_rets = benchmark_rets[benchmark_rets.index > datetime.datetime.now() - relativedelta(years=time_frame_in_years)]

        if device == settings.constants.DEVICE_TYPE_MOBILE:
            if not asset_returns.empty:
                try:
                    fig = tears.create_returns_tear_sheet(asset_returns.squeeze(
                    ), benchmark_rets=benchmark_rets.squeeze(), return_fig=True, sravzid=name)
                    file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
                    self.logger.info(
                        'Portfolio returns tear sheet created: {0}'.format(file_path))
                    fig.savefig(file_path)
                    plt.close(fig)
                    return "{0}.png".format(file_path)
                except Exception:
                    self.logger.exception(
                        'Error plotting portfolio retruns tear sheet')
                    return None
            return None
        else:
            raise NotImplementedError

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def portfolio_returns_timeseries_analysis(self, name,  user_id, portfolio_assets=None, time_frame_in_years=10, index='idx_us_gspc', upload_to_aws=False, device=settings.constants.DEVICE_TYPE_MOBILE):
        '''
            # In years
            sravzids = ['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']
            pcae.get_portfolio_pca(sravzids)
        '''
        portofolio_cummulative_returns = self.get_portfolio_cummulative_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        if device == settings.constants.DEVICE_TYPE_MOBILE:
            if not portofolio_cummulative_returns.empty:
                try:
                    #self.logger.info("Portfolio timeseries analysis done")
                    returns_df = portofolio_cummulative_returns.to_frame().replace([np.inf, -np.inf], np.nan).ffill()
                    returns_df.columns = ['Returns']
                    return self.tse.get_ts_data("Portfolio", returns_df, "Returns")
                except Exception:
                    self.logger.exception('Error in portoflio timeseries analysis')
                    return None
            return None
        else:
            raise NotImplementedError

    def get_stocker_tear_sheet(self, portfolio_name, returns_df, chart_type, number_of_years_back = 10):
        '''
            # Returns stocker analysis
        '''
        return stocker_tears.create_stocker_tear_sheet(None, chart_type, asset_name = portfolio_name, returns_df = returns_df, number_of_years_back = number_of_years_back)

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_predict_future(self, name,  user_id, portfolio_assets=None, start_date = None, end_date = None,
                       index='idx_us_gspc',
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        portofolio_cummulative_returns = self.get_portfolio_cummulative_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        try:
            #self.logger.info("Portfolio timeseries analysis done")
            returns_df = portofolio_cummulative_returns.to_frame().replace([np.inf, -np.inf], np.nan).ffill()
            returns_df.columns = ['Returns']
            return self.get_stocker_tear_sheet(name, returns_df, stocker_tears.CHART_TYPE_PREDICT_FUTURE, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for portfolio %s username %s" % (name, user_id), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_prophet_model(self, name,  user_id, portfolio_assets=None, start_date = None, end_date = None,
                       index='idx_us_gspc',
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        portofolio_cummulative_returns = self.get_portfolio_cummulative_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        try:
            #self.logger.info("Portfolio timeseries analysis done")
            returns_df = portofolio_cummulative_returns.to_frame().replace([np.inf, -np.inf], np.nan).ffill()
            returns_df.columns = ['Returns']
            return self.get_stocker_tear_sheet(name, returns_df, stocker_tears.CHART_TYPE_CREATE_PROPHET_MODEL, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for portfolio %s username %s" % (name, user_id), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_evaluate_prediction(self, name,  user_id, portfolio_assets=None, start_date = None, end_date = None,
                       index='idx_us_gspc',
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        portofolio_cummulative_returns = self.get_portfolio_cummulative_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        try:
            #self.logger.info("Portfolio timeseries analysis done")
            returns_df = portofolio_cummulative_returns.to_frame().replace([np.inf, -np.inf], np.nan).ffill()
            returns_df.columns = ['Returns']
            return self.get_stocker_tear_sheet(name, returns_df, stocker_tears.CHART_TYPE_EVALUATE_PREDICTION, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for portfolio %s username %s" % (name, user_id), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_change_point_prior_analysis(self, name,  user_id, portfolio_assets=None, start_date = None, end_date = None,
                       index='idx_us_gspc',
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        portofolio_cummulative_returns = self.get_portfolio_cummulative_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        try:
            #self.logger.info("Portfolio timeseries analysis done")
            returns_df = portofolio_cummulative_returns.to_frame().replace([np.inf, -np.inf], np.nan).ffill()
            returns_df.columns = ['Returns']
            return self.get_stocker_tear_sheet(name, returns_df, stocker_tears.CHART_TYPE_CHANGE_POINT_PRIOR_ANALYSIS, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for portfolio %s username %s" % (name, user_id), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_change_point_prior_validation(self, name,  user_id, portfolio_assets=None, start_date = None, end_date = None,
                       index='idx_us_gspc',
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        portofolio_cummulative_returns = self.get_portfolio_cummulative_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        try:
            #self.logger.info("Portfolio timeseries analysis done")
            returns_df = portofolio_cummulative_returns.to_frame().replace([np.inf, -np.inf], np.nan).ffill()
            returns_df.columns = ['Returns']
            return self.get_stocker_tear_sheet(name, returns_df, stocker_tears.CHART_TYPE_CHANGE_POINT_PRIOR_VALIDATION, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for portfolio %s username %s" % (name, user_id), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_stocker_tear_sheet_create_prediciton_with_change_point(self, name,  user_id, portfolio_assets=None, start_date = None, end_date = None,
                       index='idx_us_gspc',
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns stocker analysis
        '''
        portofolio_cummulative_returns = self.get_portfolio_cummulative_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        try:
            #self.logger.info("Portfolio timeseries analysis done")
            returns_df = portofolio_cummulative_returns.to_frame().replace([np.inf, -np.inf], np.nan).ffill()
            returns_df.columns = ['Returns']
            return self.get_stocker_tear_sheet(name, returns_df, stocker_tears.CHART_TYPE_EVALUATE_PREDICTION_WITH_CHANGE_POINT, number_of_years_back = number_of_years_back)
        except Exception:
            self.logger.error("Error plotting stocker_tear_sheet for portfolio %s username %s" % (name, user_id), exc_info=True)
            return None

    @aws_cache.save_file_to_s3
    @helper.concat_n_images
    def get_correlation_analysis_tear_sheet(self, name,  user_id, portfolio_assets=None, start_date = None, end_date = None,
                       index='idx_us_gspc',
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns correlation analysis
        '''
        portofolio_assets_daily_returns = self.get_portfolio_assets_daily_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        portofolio_daily_returns = self.get_portfolio_daily_returns(
            name, user_id, portfolio_assets=portfolio_assets).tz_localize('UTC', level=0)
        try:
            portfolio_correlation_report_path = helper.save_plt(tears.create_portfolio_correlation_report(portofolio_assets_daily_returns, portofolio_daily_returns, return_fig = True))
            portfolio_correlation_matrix_report_path = helper.save_plt(tears.create_portfolio_correlation_matrix_report(portofolio_assets_daily_returns,return_fig = True))
            return [portfolio_correlation_report_path, portfolio_correlation_matrix_report_path]
        except Exception:
            self.logger.error("Error plotting correlation analysis for portfolio %s username %s" % (name, user_id), exc_info=True)
            return None


    @helper.save_data_to_contabo
    def get_correlation_analysis_tear_sheet_user_asset(self, sravz_id,
                       number_of_years_back = 10,
                       upload_to_aws = False,
                       device = settings.constants.DEVICE_TYPE_PC):
        '''
            # Returns correlation analysis
            from src.analytics.portfolio import engine
            e = engine()
            e.get_correlation_analysis_tear_sheet_user_asset('data_undefined_daily-treasury-rates.csv_1670196582998')
        '''
        pe = price_queries.engine()
        df = pe.get_df_from_s3(sravz_id)
        return [df.corr().to_html(), f'{settings.constants.CONTABO_BUCKET_PREFIX}/user_assets/correlation/{sravz_id}.html'], {'gzip_data':False, 'ContentType':'text/html; charset=utf-8'}
        
if __name__ == '__main__':
    e = engine()
    e.get_correlation_analysis_tear_sheet_user_asset('data_undefined_daily-treasury-rates.csv_1670196582998')
