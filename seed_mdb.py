#!/usr/bin/env python
import pymongo
from src.services import mdb
from src.services.assets import exchanges as sravz_assets_exchanges
mdbe = mdb.engine()
# Create indexes
mdbe.create_unique_index_collection([ ("date", pymongo.ASCENDING), ("statistic", pymongo.ASCENDING)], "economic_calendar", key_name='economic_calendar_date_statistic_uidx')
mdbe.create_unique_index_collection([ ("Ticker", pymongo.ASCENDING)], "quotes_stocks", key_name= 'quotes_stocks_ticker_unique_index')
mdbe.create_unique_index_collection([ ("fullName", pymongo.ASCENDING), ("email", pymongo.ASCENDING)], "users", key_name= 'users_full_name_email_unique_index')
mdbe.create_unique_index_collection([ ("datetime", pymongo.ASCENDING)], "rss_feeds", key_name='rss_feeds_datetime_idx')
mdbe.create_unique_index_collection([ ("report_date", pymongo.ASCENDING)], "earnings", key_name='earning_report_date_idx')
mdbe.create_unique_index_collection([ ("date", pymongo.ASCENDING)], "economic_events", key_name='economic_events_date_delete_after_one_month_idx', unique=False, expireAfterSeconds=2628000) # 1 Month
mdbe.create_unique_index_collection([ ("SravzId", pymongo.ASCENDING)], "assets_exchange_symbols", key_name='assets_exchange_symbols_sravz_id_idx')
mdbe.create_unique_index_collection([ ("Country", pymongo.ASCENDING), ("Exchange", pymongo.ASCENDING)], "assets_exchange_symbols", key_name='assets_exchange_symbols_country_exchange_idx')


sravz_assets_exchanges.upload_world_capitals()

'''
db.messages_wip.createIndex( {date: 1}, {
    expireAfterSeconds: 172800, // 2 days
    partialFilterExpression: {
        scheduledDate: 0
    }
});
db.nsq_message_cache.createIndex( {date: 1}, {
    expireAfterSeconds: 172800, // 2 days
    partialFilterExpression: {
        scheduledDate: 0
    }
});
db.s3_presigned_urls.createIndex( {createdDate: 1}, {
    expireAfterSeconds: 15552000, // 6 months
    partialFilterExpression: {
        scheduledDate: 0
    }
});
'''