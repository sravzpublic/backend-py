#!/usr/bin/python

import feedparser, datetime, requests, io
from src.util.settings import constants
from src.util import settings, logger
from src.services import mdb
from src.analytics import nltk
from dateutil import parser, tz
import pytz
utc=pytz.UTC

class engine(object):
    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    def upload_rss_feeds_to_db(self, data, collection_name):
        mdbe = mdb.engine()
        rss_feeds_collection = mdbe.get_collection(collection_name)
        for item in data:
            # Check feed was in last 30 mins. Crontab runs every 15 mins
            feed_dt = parser.parse(item.published)
            if feed_dt > (datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=constants.FEEDS_TO_PROCESS_WITH_LAST_MINS)):
                item['datetime'] = parser.parse(item.published)
                item['sentiment'] = nltk.sentiment_scores(item.get('title'))
                rss_feeds_collection.update_one({"id": item['id'], "datetime": item['datetime']}, {"$set": item}, upsert=True)

    def upload_feeds(self):
        for url in constants.FEED_URLS.values():
            self.logger.info("Processing url: {0}".format(url))
            # Do request using requests library and timeout
            try:
                resp = requests.get(url, timeout=20.0)
            except:
                self.logger.warn("Timeout when reading RSS %s", url)
            # Put it to memory stream object universal feedparser
            content = io.BytesIO(resp.content)
            # Parse content
            feed = feedparser.parse(content)
            feed = feedparser.parse(url)
            self.upload_rss_feeds_to_db(feed.entries, constants.FEEDS_COLLECTION)
