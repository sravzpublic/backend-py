import datetime, msgpack, json, time, hashlib, pytz, traceback
import pandas as pd

from src.analytics import stats, pca, risk, charts, portfolio, timeseries
from src.services.cache import Cache
from src.services import aws, price, ecocal, mdb
from src.services.stock import db_upload as stock_db_upload
from src.services.stock import historical_quotes as stock_historical_quotes
from src.services.bond import historical_quotes as bond_historical_quotes
from src.services.currency import db_upload as currency_db_upload
from src.services.currency import historical_db_upload as currency_historical_db_upload
from src.services.crypto import db_upload as crypto_db_upload
from src.services.crypto import historical_db_upload as crypto_historical_db_upload
from src.services.vix import db_upload as vix_db_upload
from src.services.vix import historical_db_upload as vix_historical_db_upload
from src.services.rss import parser
from src.util import settings, logger, helper
from src.services.etfs import quotes as etf_quotes
from src.services.etfs import historical_db_upload_index_quotes
from src.services.assets import db_upload as sravz_assets_db_upload
from src.services.assets import db_s3_upload_index_components, db_s3_upload_exchange_components
from src.analytics import pnl
from src.services.rates import db_upload as rates_db_upload
from src.services.rates import historical_db_upload as rates_historical_db_upload
from src.services import price, upload_historical_commodity_quotes_to_historical_mdb
from src.services.earnings import db_upload as earnings_db_upload
from src.services.assets.exchanges import upload_exchange_symbol_list
from src.services.dashboard import upload_from_db_to_s3
from src.analytics import spread

class MessageContracts(object):
    """
        Parse Sravz Message and hendle the message
        To Add a New Message Contract
            1. Add global engine
            2. Add message ID to function name mapping
    """
    STATS_ENGINE = stats.engine()
    PCA_ENGINE = pca.engine()
    RISK_ENGINE = risk.engine()
    CHARTS_ENGINE = charts.engine()
    PORTFOLIO_ENGINE = portfolio.engine()
    TIMESERIES_ENGINE = timeseries.engine()
    FEED_PARSE_ENGINE = parser.engine()
    PRICE_ENGINE = price.engine()
    ECO_CAL_ENGINE = ecocal.engine()
    ETF_ENGINE = etf_quotes.engine()
    PNL_ENGINE = pnl.engine()
    EARNINGS_ENGINE = earnings_db_upload.engine()
    STOCK_HISTORICAL_QUOTES_ENGINE = stock_historical_quotes.engine()
    BOND_HISTORICAL_QUOTES_ENGINE = bond_historical_quotes.engine()
    MDBE = mdb.engine()
    DASHBOARD_ENGINE = upload_from_db_to_s3.engine()

    LOGGER = logger.RotatingLogger(__name__).getLogger()

    CRON_MESSAGES_MIN_ID = 23
    CRON_MESSAGES_MAX_ID = 49
    UPLOAD_CRON_NSQ_PROCESSED_REPORT = 44

    MESSAGEID_FUNCTION_MAP = {
        1: STATS_ENGINE.get_dickey_fuller_stats,
        2: STATS_ENGINE.get_historical_rolling_stats_by_week,
        3: STATS_ENGINE.get_historical_rolling_stats_by_month,
        4: STATS_ENGINE.get_historical_rolling_stats_by_year,
        1.1: STATS_ENGINE.get_rollingstats_tear_sheet,
        5: PCA_ENGINE.get_scatter_plot_daily_return,
        6: PCA_ENGINE.get_pca_components,
        6.1: PCA_ENGINE.get_pca_components_vs_index_returns,
        6.2: PCA_ENGINE.create_portfolio_pca_report,
        7: PCA_ENGINE.get_covariance_matrix,
        8: RISK_ENGINE.get_risk_stats,
        9: CHARTS_ENGINE.get_combined_chart,
        9.1: CHARTS_ENGINE.get_combined_chart_image,
        10: STATS_ENGINE.get_rolling_stats_by_sravz_id,
        11: STATS_ENGINE.get_df_test_by_sravz_id,
        12: STATS_ENGINE.get_rolling_stats_by_sravz_id_timeframe,
        13: STATS_ENGINE.get_df_stats_by_sravz_id,
        14: RISK_ENGINE.get_returns_tear_sheet,
        15: PORTFOLIO_ENGINE.create_portfolio_returns_tear_sheet,
        16: TIMESERIES_ENGINE.get_ts_analysis,
        17: PORTFOLIO_ENGINE.portfolio_returns_timeseries_analysis,
        18: RISK_ENGINE.get_bayesian_tear_sheet,
        19.1: RISK_ENGINE.get_stocker_tear_sheet_create_prophet_model,
        19.2: RISK_ENGINE.get_stocker_tear_sheet_create_evaluate_prediction,
        19.3: RISK_ENGINE.get_stocker_tear_sheet_create_change_point_prior_analysis,
        19.4: RISK_ENGINE.get_stocker_tear_sheet_create_change_point_prior_validation,
        19.5: RISK_ENGINE.get_stocker_tear_sheet_create_prediciton_with_change_point,
        19.6: RISK_ENGINE.get_stocker_tear_sheet_predict_future,
        20.1: PORTFOLIO_ENGINE.get_stocker_tear_sheet_create_prophet_model,
        20.2: PORTFOLIO_ENGINE.get_stocker_tear_sheet_create_evaluate_prediction,
        20.3: PORTFOLIO_ENGINE.get_stocker_tear_sheet_create_change_point_prior_analysis,
        20.4: PORTFOLIO_ENGINE.get_stocker_tear_sheet_create_change_point_prior_validation,
        20.5: PORTFOLIO_ENGINE.get_stocker_tear_sheet_create_prediciton_with_change_point,
        20.6: PORTFOLIO_ENGINE.get_stocker_tear_sheet_predict_future,
        21: PORTFOLIO_ENGINE.get_correlation_analysis_tear_sheet,
        21.1: PORTFOLIO_ENGINE.get_correlation_analysis_tear_sheet_user_asset,
        22: CHARTS_ENGINE.get_crypto_tearsheet,
        #### Start CronJobs
        # Keep cron messages in this range, report generated
        CRON_MESSAGES_MIN_ID: FEED_PARSE_ENGINE.upload_feeds,
        24: PRICE_ENGINE.get_eodhistoricaldata_live_future_quotes,
        25: ECO_CAL_ENGINE.get_current_week_eco_cal_from_web,
        # Index quotes
        26: ETF_ENGINE.get_eodhistoricaldata_index_quotes,
        27: sravz_assets_db_upload.upload,
        28: PNL_ENGINE.update,
        29: rates_db_upload.upload,
        30: PRICE_ENGINE.get_eodhistoricaldata_historical_future_quotes,
        31: db_s3_upload_index_components.upload,
        32: db_s3_upload_exchange_components.upload,
        33: stock_db_upload.upload,
        34: currency_db_upload.upload,
        35: crypto_db_upload.upload,
        36: vix_db_upload.upload,
        37: upload_historical_commodity_quotes_to_historical_mdb.upload,
        38: rates_historical_db_upload.upload,
        # Historical Index Quotes
        39: historical_db_upload_index_quotes.upload_historical_quotes,
        40: currency_historical_db_upload.upload,
        41: crypto_historical_db_upload.upload,
        42: vix_historical_db_upload.upload,
        43: helper.empty_cache_if_new_day,
        44: "MessageContracts.upload_cron_messages_processed_report",
        45: EARNINGS_ENGINE.get_current_week_earnings_from_web,
        46: STOCK_HISTORICAL_QUOTES_ENGINE.get_eodhistoricaldata_historical_stock_quotes,
        47: upload_exchange_symbol_list,
        48: DASHBOARD_ENGINE.upload,
        CRON_MESSAGES_MAX_ID: BOND_HISTORICAL_QUOTES_ENGINE.get_eodhistoricaldata_historical_bond_quotes,
        #### End CronJobs
        49: spread.perform_spread_analysis_for_assets
    }


    CACHE_KEY_IN_PROGRESS_MESSAGES = 'MESSAGE_PROCESSING_IN_PROGRESS'

    def __init__(self):
        """
        """
        super(MessageContracts, self).__init__()

    def parse(self, msg):
        """
            Contains incoming message from Kafka
        """
        pass

    @staticmethod
    def get_input_message(msg_in):
        """
            Perform decoding and understand the message
            # Message format
            {
                #Message identifier
                id: number
                #Input params
                p_i:
                #Topic on which to send output data
                t_o:
                #Output data
                d_o:
            }
            msg_in = '{"id": 1, "p_i": {"args": ["fut_gold_feb_17_usd_lme"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "", "d_o": null}'
        """
        #data = json.loads(msg_in.lower())
        data = json.loads(msg_in)
        if data:
            return data
        return "Input request error"

    # @staticmethod
    # def get_messages_in_progress(collection_name = 'messages_wip'):
    #     try:
    #         value = Cache.Instance().get(MessageContracts.CACHE_KEY_IN_PROGRESS_MESSAGES)
    #         if value:
    #             MessageContracts.LOGGER.info('Following messages are being processed: {0}'.format(str(value)))
    #             return value
    #     except Exception:
    #         MessageContracts.LOGGER.exception('No message in progress')
    #     return None

    @staticmethod
    def set_message_in_progress(cache_key, msg, exception_message, status, collection_name = 'messages_wip'):
        '''
            There is potential of the same message to be process concurrently but that is rare
        '''
        try:
            # Update MDB
            messages_wip_collection = MessageContracts.MDBE.get_collection(collection_name)
            try:
                message = {}
                message['key'] = cache_key
                message['date'] = datetime.datetime.now(datetime.UTC)
                message['status'] = status
                message['msg'] = msg
                message['exception_message'] = exception_message
                messages_wip_collection.update_one({"key": message['key']}, {
                    "$set": message}, upsert=True)
                MessageContracts.LOGGER.info(f"Message WIP uploaded to MDB {collection_name} - msg {message}")
            except Exception:
                MessageContracts.LOGGER.error('Failed to update message wip to mdb {0}'.format(cache_key), exc_info=True)

            MessageContracts.LOGGER.info('Updated message: {0} state to {1}'.format(cache_key, status))
        except Exception:
            MessageContracts.LOGGER.exception('Unable to set message in progress')

    @staticmethod
    def is_message_in_progress(cache_key, collection_name = 'messages_wip'):
        try:
            messages_wip_collection = MessageContracts.MDBE.get_collection(collection_name)
            try:
                # Get message in progress for today only.
                messages = MessageContracts.MDBE.get_collection_items(collection_name, iterator = False, find_clause={"key": { "$in": [cache_key]}, "date": {"$gte": datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)}})
                if messages:
                    message = messages.pop()
                    if message and 'status' in message:
                        return message.get('status')
            except Exception:
                MessageContracts.LOGGER.error('Failed to get message status from MDB {0}'.format(cache_key), exc_info=True)

            return False
        except Exception:
            MessageContracts.LOGGER.exception('Unable to set message in progress')

    @staticmethod
    def get_message_from_cache(cache_key, collection_name = 'nsq_message_cache'):
        try:
            value = Cache.Instance().get(cache_key)
            if value:
                MessageContracts.LOGGER.info(
                    'Message found in cache: key: {0} - message: {1}'.format(cache_key, str(value)))
                return helper.convert(value)
            else:
                MessageContracts.LOGGER.info(
                    'Message not found in cache: key: {0}'.format(cache_key))
        except Exception:
            MessageContracts.LOGGER.exception(
                'Error retrieving message from cache for cache key: %s' % (cache_key))

        # Get message from MDB
        nsq_message_cache_collection = MessageContracts.MDBE.get_collection(collection_name)
        try:
            messages = MessageContracts.MDBE.get_collection_items(collection_name, iterator = False, find_clause={"key": { "$in": [cache_key]}, "date": {"$gte": datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)}})
            if messages:
                message = messages.pop()
                del message['_id']
                del message['date']
                MessageContracts.LOGGER.info(
                    'Message found in mdb cache: key: {0} - message: {1}'.format(cache_key, str(message)))
                return message
        except Exception:
            MessageContracts.LOGGER.error('Failed to get message from mdb cache {0}'.format(cache_key), exc_info=True)

        return None

    @staticmethod
    def get_cron_messages_processed_report(collection_name = 'nsq_message_cache'):
        '''
            Returns last 24 hours cron messages processed report
        '''
        # Get message from MDB
        nsq_message_cache_collection = MessageContracts.MDBE.get_collection(collection_name)
        today = datetime.datetime.now(datetime.UTC).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        yesterday = (today - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        try:
            messages = MessageContracts.MDBE.get_collection_items(
                collection_name,
                iterator = False,
                find_clause={
                    "date": {
                        "$gte": yesterday
                    }
            }
            )
            if messages:
                df = pd.DataFrame.from_dict(messages)
                df = df[(df['id'] >= MessageContracts.CRON_MESSAGES_MIN_ID)&(df['id'] <= MessageContracts.CRON_MESSAGES_MAX_ID)][['id','date','e']].groupby(['id']).agg(['unique','count','min','max'])
                report_dict = df.to_dict()
                del report_dict[('e', 'unique')]
                del report_dict[('date', 'unique')]
                report_dict_updated = {}
                for key in report_dict:
                    value = report_dict[key]
                    report_dict_updated["-".join(key).strip("-")] = value
                report_df = pd.DataFrame.from_dict(report_dict_updated)
                report_df.reset_index(inplace=True)
                report_df = report_df.rename(columns = {'index':'message_id'})
                report_df['id-report-date'] = ["{0}-{1}".format(message_id, today.strftime("%m-%d-%Y")) for  message_id in report_df['message_id']]
                return report_df.to_dict('records')
        except Exception:
            MessageContracts.LOGGER.error('Failed to generate report', exc_info=True)
        return None

    @staticmethod
    def upload_cron_messages_processed_report(collection_name = 'cron_nsq_message_report'):
        '''
            Uploads cron processed message report to mdb
        '''
        report_data = MessageContracts.get_cron_messages_processed_report()
        print(report_data)
        if report_data:
            for message in report_data:
                value_id = message['message_id']
                try:
                    message['name'] = "{0}.{1}".format(MessageContracts.MESSAGEID_FUNCTION_MAP.get(value_id).__module__,MessageContracts.MESSAGEID_FUNCTION_MAP.get(value_id).__name__)
                except:
                    MessageContracts.LOGGER.error(f"Failed to get function name for id {value_id}", exc_info=True)
                    message['name'] = MessageContracts.MESSAGEID_FUNCTION_MAP.get(value_id)
                print(message)
            MessageContracts.MDBE.upsert_to_collection(collection_name, report_data, upsert_clause_field = 'id-report-date')
        else:
            MessageContracts.LOGGER.warn('No cron messages processed report to upload')


    @staticmethod
    def upload_message_to_mdb(key, message, exception_message, collection_name = 'nsq_message_cache'):
        nsq_message_cache_collection = MessageContracts.MDBE.get_collection(collection_name)
        try:
            message['date'] = datetime.datetime.now(datetime.UTC)
            message['key'] = key
            message['exception_message'] = exception_message
            nsq_message_cache_collection.insert_one(message)
            MessageContracts.LOGGER.info(f"Message uploaded to MDB collection: {collection_name} - Msg {message}")
            del message['date']
            del message['_id']
        except Exception:
            MessageContracts.LOGGER.error('Failed to update message to db {0}'.format(key), exc_info=True)

    @staticmethod
    def get_output_message(msg):
        """
            from src.services.kafka_helpers.message_contracts import MessageContracts
            import json
            #Perform enconding and create the response message
            msg_in = '{"id": 1, "p_i": {"args": ["fut_gold_feb_17_usd_lme"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "", "d_o": null}'
            msg = json.loads(msg_in.lower())
            MessageContracts.get_output_message(msg)
            msg_in = '{"id": 2, "p_i": {"args": ["fut_gold_feb_17_usd_lme", "mean"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "", "d_o": null}'
            msg = json.loads(msg_in.lower())
            MessageContracts.get_output_message(msg)
            msg_in = '{"id": 4, "p_i": {"args": ["fut_gold_feb_17_usd_lme", "std"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "", "d_o": null}'
            msg_in = '{"id": 4, "p_i": {"args": ["fut_platinum_feb_17_usd_lme", "std"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "", "d_o": null}'
            msg_in = '{"id": 5, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}'
            msg_in = '{"id": 5, "p_i": {"args": [["stk_us_AYI", "stk_us_AXP", "stk_us_AWK", "stk_us_AZO", "stk_us_AVB", "stk_us_AVY", "stk_us_AVG"]], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}'
            msg_in = '{"id": 6, "p_i": {"args": [['fut_gold_feb_17_usd_lme', 'fut_silver_feb_17_usd_lme']], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}'
            msg_in = '{"id": 7, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": false}, "t_o": "portfolio1", "d_o": null}'
            msg_in = '{"id": 8, "p_i": {"args": ["stk_us_FB"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": false}, "t_o": "portfolio1", "d_o": null}'
            msg_in = '{"id": 9, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": false}, "t_o": "portfolio1", "d_o": null}'
            msg_in = '{"id": 21.1, "p_i": {"args": ["data_undefined_nike_srbounce_v2_list_of_trades_2022-11-26.csv_1669569679677"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": false}, "t_o": "portfolio1", "d_o": null}'
            msg = json.loads(msg_in.lower())
            MessageContracts.get_output_message(msg)
        """
        helper.empty_cache_if_new_day()
        cache_key = helper.get_md5_of_string("get_output_message_{0}_{1}_{2}".format(
            msg.get("id"), msg["p_i"]["args"], msg["p_i"]["kwargs"]))
        exception_message = ""

        # If the message already processed, return the message from the cache
        if msg.get("cache_message"):
            cached_message = MessageContracts.get_message_from_cache(cache_key)
            if cached_message:
                return cached_message
        else:
            MessageContracts.LOGGER.debug(
                'Cache ignored for key {0} cache_message set to: {1}'.format(cache_key, msg.get("cache_message")))

        if not MessageContracts.is_message_in_progress(cache_key):
            MessageContracts.set_message_in_progress(cache_key, msg, exception_message, True)
            if msg and msg.get("id") != None:
                if MessageContracts.MESSAGEID_FUNCTION_MAP.get(msg.get("id")):
                    msg["ts"] = time.time()
                    try:
                        # If it's an internal message
                        if msg.get("id") == MessageContracts.UPLOAD_CRON_NSQ_PROCESSED_REPORT:
                            msg["fun_n"] = "MessageContracts.upload_cron_messages_processed_report"
                            MessageContracts.upload_cron_messages_processed_report()
                        else:
                            # Set the function name for easy display on the UI
                            msg["fun_n"] = MessageContracts.MESSAGEID_FUNCTION_MAP.get(
                                msg.get("id")).__name__
                            data = MessageContracts.MESSAGEID_FUNCTION_MAP.get(
                                msg.get("id"))(*msg["p_i"]["args"], **msg["p_i"]["kwargs"])
                            # If data is uploaded to AWS do not resend in NSQ message response
                            if msg.get("p_i").get("kwargs").get("upload_to_aws"):
                                data["data"] = None
                            msg["d_o"] = data
                        # No error message
                        msg["e"] = ""
                    except Exception as e:
                        exception_message = traceback.format_exc()
                        MessageContracts.LOGGER.exception(
                            'Error processing message: %s' % (str(msg)))
                        msg["e"] = "Error"
                else:
                    msg["e"] = "Message ID not supported. Available message IDs %s, given ID %s, given message %s" % (
                        str(list(MessageContracts.MESSAGEID_FUNCTION_MAP.keys())), msg.get("id"), str(msg))
            else:
                msg["e"] = "Input message is empty or message ID not provided, given message %s" % (
                    str(msg))
            if not msg.get("e") and msg.get("cache_message"):
                try:
                    Cache.Instance().add(cache_key, msg)
                    MessageContracts.LOGGER.debug(
                        'Saved message to cache: key: {0} - message: {1}'.format(cache_key, str(msg)))
                except Exception as e:
                    exception_message = str(e)
                    MessageContracts.LOGGER.exception(
                        'Could not add message to cache: %s' % (str(msg)))
            else:
                MessageContracts.LOGGER.info(
                    'Message not saved to Cache. cache_message: {0} with cache: key: {1} - message: {2}'.format(msg.get("cache_message"),
                    cache_key, str(msg)))
            # Upload all messages to mdb
            MessageContracts.upload_message_to_mdb(cache_key, msg, exception_message)
            MessageContracts.LOGGER.debug(
                'Saved message to mdb: key: {0} - message: {1}'.format(cache_key, str(msg)))
            MessageContracts.set_message_in_progress(cache_key, msg, exception_message, False)
        else:
            msg["e"] = "Given message %s is being processed. Please check after sometime" % (
                    str(msg))
            MessageContracts.LOGGER.info("Message being processed for cache_key {0}".format(cache_key))
        return msg


if __name__ == '__main__':
    # Spread analysis ID: 49
    msg_in = '{"id": 49, "p_i": {"args": ["fut_us_gc", "idx_us_gspc"], "kwargs": {}}, "k_i": {"return_aws_info_only": false}, "t_o": "portfolio1", "d_o": null}'
    msg = json.loads(msg_in.lower())
    MessageContracts.get_output_message(msg)

