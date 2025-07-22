import datetime
import uuid
import pandas as pd
from src.util import settings, helper
from src.services import price_queries
from src.services import mdb
from src.services import aws
from src.util import aws_cache, logger
import matplotlib.pyplot as plt
from src.analytics import tears, world_indices_tears, crypto_tears
plt.ioff()
pd.plotting.register_matplotlib_converters()

class engine(object):
    """Performs statistical operations on the df"""

    def __init__(self):
        self.aws_engine = aws.engine()
        self.weekly = 5
        self.monthly = 22
        self.yearly = 255
        self.pqe = price_queries.engine()
        self.aws_cache_engine = aws_cache.engine()
        self.mdbe = mdb.engine()

    def get_combined_chart(self, sravzids, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_PC):
        '''
            from src.analytics.charts import engine
            ce = engine()
            ce.get_combined_chart(['fut_gold_feb_17_usd_lme', 'fut_oil'])
        '''
        # Use class + function name for key
        key = 'charts_get_combined_chart'
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravzid) for sravzid in sravzids]
        # Check key length limitation
        cache_key = aws_key = "%s_%s_%s" % (
            key, "_".join(sravz_generic_ids), device)
        # Change bucket name if required
        bucket_name = settings.constants.charts_bucket_name

        def data_function():
            firstDf = None
            firstSravzID = None
            for sravzid in sravzids:
                try:
                    sravz_generic_id = helper.get_generic_sravz_id(sravzid)
                    price_df = self.pqe.get_historical_price_df(sravz_generic_id)
                    column_names = {}
                    [column_names.update({name: "%s%s" % (name, sravz_generic_id)}) for name in price_df.columns]
                    price_df = price_df.rename(index=str, columns=column_names)
                    if not firstSravzID:
                        firstDf = price_df
                        firstSravzID = sravzid
                        continue
                    else:
                        firstDf = firstDf.join(price_df, how='outer')
                except:
                    logger.logging.exception(
                        'Failed to process sravz_id: {0}'.format(sravzid))                    
            if device == settings.constants.DEVICE_TYPE_MOBILE:
                fig = plt.figure()
                plt.close(fig)
                firstDf.index = pd.to_datetime(firstDf.index)
                # pylint: disable=E1127
                data_files = {}
                for key, value in settings.constants.ChartsToDisplayAndAcceptedColumns.items():
                    # Plot Settle for Futures and Last for Stocks on the same plot
                    df_to_plot = firstDf[settings.constants.DEVICE_TYPE_MOBILE_CHARTS_START_DATE:datetime.date.today(
                    )][[x for x in firstDf.columns if any([y for y in value if y in x.lower()])]]
                    if not df_to_plot.empty:
                        try:
                            df_to_plot.plot(kind='line')
                            file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
                            plt.savefig(file_path)
                            data_files[key] = "{0}.png".format(file_path)
                        except Exception:
                            logger.logging.exception('Error plotting data for columns {0}'.format([
                                x for x in firstDf.columns if key in x.lower()]))
                            data_files[key] = None
                    else:
                        data_files[key] = None
                return data_files
            else:
                firstDf = firstDf.fillna(method="ffill")
                return firstDf
        return self.aws_cache_engine.handle_cache_aws(cache_key, bucket_name,
                                                      aws_key, data_function, upload_to_aws)

    def get_combined_chart_image(self, sravzids, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_MOBILE):
        '''
            from src.analytics.charts import engine
            ce = engine()
            ce.get_combined_chart_image(['fut_gold_feb_17_usd_lme', 'fut_oil'])
        '''
        # Use class + function name for key
        key = 'charts_get_combined_chart'
        sravz_generic_ids = [helper.get_generic_sravz_id(
            sravzid) for sravzid in sravzids]
        # Check key length limitation
        cache_key = aws_key = "%s_%s_%s" % (
            key, "_".join(sravz_generic_ids), device)
        # Change bucket name if required
        bucket_name = settings.constants.charts_bucket_name

        def data_function():
            if device == settings.constants.DEVICE_TYPE_MOBILE:
                firstDf = None
                firstSravzID = None
                for sravzid in sravzids:
                    sravz_generic_id = helper.get_generic_sravz_id(sravzid)
                    price_df = self.pqe.get_historical_price_df(sravz_generic_id)
                    column_names = {}
                    [column_names.update({name: "%s%s" % (name, sravz_generic_id)}) for name in price_df.columns]
                    price_df = price_df.rename(index=str, columns=column_names)
                    if not firstSravzID:
                        firstDf = price_df
                        firstSravzID = sravzid
                        continue
                    else:
                        firstDf = firstDf.join(price_df)
                fig = plt.figure()
                plt.close(fig)
                firstDf.index = pd.to_datetime(firstDf.index)
                # pylint: disable=E1127
                data_files = {}
                fig = tears.get_combined_charts(sravzids, return_fig=True)
                file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
                logger.logging.info(
                    'Combined charts file path: {0}'.format(file_path))
                fig.savefig(file_path)
                plt.close(fig)
                data_files['combined_chart'] = "{0}.png".format(file_path)
                return data_files
            else:
                charts_dfs = []
                firstSravzID = None
                # firstdf = None
                smallestDF = None
                modifiedDFs = []
                try:
                    for sravzid in sravzids:
                        sravz_generic_id = helper.get_generic_sravz_id(sravzid)
                        price_df = self.pqe.get_historical_price_df(sravz_generic_id)
                        #TODO: Ignite UI datasource requirement
                        if not firstSravzID:
                            firstSravzID = sravzid
                            smallestDF = price_df
                        else:
                            if len(price_df) < len(smallestDF):
                                smallestDF = price_df
                            # price_df = price_df[price_df.index.isin(firstdf.index)]
                        price_df.index.names = ['time']
                        price_df = price_df.rename(str.lower,  axis='columns')
                        if 'adjustedclose' in price_df.columns and price_df['adjustedclose'].any():
                            price_df = price_df.rename(columns={"adjustedclose": "close"})
                        elif 'settle' in price_df.columns and price_df['settle'].any():
                            price_df = price_df.rename(columns={"settle": "close"})
                        elif 'last' in price_df.columns and price_df['last'].any():
                            price_df = price_df.rename(columns={"last": "close"})
                        modifiedDFs.append((sravz_generic_id, price_df))
                except:
                    logger.logging.exception(
                        'Failed to process sravz_id: {0}'.format(sravzid))                         
                for sravz_generic_id, price_df in modifiedDFs:
                    price_df = price_df[price_df.index.isin(smallestDF.index)]
                    charts_dfs.append({'title': sravz_generic_id, 'result': price_df.to_json(orient='table')})
                return charts_dfs
        return self.aws_cache_engine.handle_cache_aws(cache_key, bucket_name,
                                                      aws_key, data_function, upload_to_aws)



    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_combined_charts(self, sravzid, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_MOBILE):
        try:
            return tears.get_combined_charts(sravzid, return_fig=True)
        except Exception:
            logger.logging.exception('Error plotting combined charts')
            return None
        return None

    @aws_cache.save_file_to_s3
    @helper.save_plot_to_file
    def get_crypto_tearsheet(self, sravzid, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_MOBILE):
        try:
            logger.logging.info('Called function: %s by Sector'%(sravzid))
            return crypto_tears.get_crypto_tears(None)
        except Exception:
            logger.logging.exception('Error get_crypto_tearsheet')
            return None
        return None

    @aws_cache.save_file_to_s3_monthly
    def get_index_component_bar_charts(self, sravzid, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_MOBILE):
        try:
            fig = plt.figure()
            fig = world_indices_tears.get_index_components_by_sector(sravzid, return_fig=True)
            file_path = '/tmp/{0}'.format(uuid.uuid4().hex)
            fig.savefig(file_path)
            plt.close(fig)
            return ("{0}.png".format(file_path), "{0}{1}".format(settings.constants.SRAVZ_MONTHLY_EOD_INDEX_COMPONENTS_PREFIX, sravzid))
        except Exception:
            logger.logging.exception(
                'Error plotting Index components: %s by Sector'%(sravzid))
            return None
        return None

    # switched to eod
    # @DeprecationWarning
    # def get_all_index_components_bar_charts(self):
    #     [self.get_index_component_bar_charts(sravzid) for sravzid in [
    #         'idx_us_gspc',
    #         'idx_us_rua',
    #         'idx_us_djia',
    #         'idx_us_rut',
    #         'idx_in_1',
    #         'idx_my_fbmklci',
    #         'idx_uk_ftse',
    #         'idx_dx_dax',
    #         'idx_fr_cac',
    #         'idx_xx_osebx',
    #         'idx_xx_ta100'
    #     ]]

    def get_eod_all_index_components_bar_charts(self):
        for index_asset in self.mdbe.get_collection_items(settings.constants.INDEX_ASSETS_COLLECTION):
            try:
                self.get_index_component_bar_charts(index_asset['SravzId'])
            except Exception:
                logger.logging.exception(
                    'Error plotting Index components: %s by Sector'%(index_asset['SravzId']))

if __name__ == '__main__':
    e = engine()
    print(e.get_combined_chart(['etf_us_AADR']))
