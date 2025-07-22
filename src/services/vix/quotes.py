from src.util import settings, logger, helper, country_currency_mapping
from fredapi import Fred
from src.services import mdb, aws
import itertools
import re
import datetime
import requests
import pycountry
from src.services import webcrawler
from bs4 import BeautifulSoup


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()
        self.awse = aws.engine()

    def get_vix_quotes(self, tickers, upload_to_db=False):
        '''
            get vix quotes
        '''
        tickers = tickers or settings.constants.ST_LOUIS_FRED_VIX_MAP.keys()
        quotes = []
        for ticker in tickers:
            try:
                if ticker == 'VXTYN':
                    cboe_ticker = 'TYVIX'
                else:
                    cboe_ticker = ticker.replace('CLS','')
                we = webcrawler.engine()
                tables = we.get_html_tables(None, "%s%s"%(settings.constants.VIX_QUOTES_URL, cboe_ticker), "table last-right padvertical", None)
                data = we.get_data_from_html_table_ignore_missing_tags(tables[0]) + we.get_data_from_html_table_ignore_missing_tags(tables[1])
                quote = {}
                for item in data:
                    quote[item[0]] = item[1]
                # Rename columns
                quote['Last'] = helper.util.getfloat(quote.pop('Last Sale'))
                quote['Change'] = helper.util.getfloat(quote.pop('Net Change'))
                quote['PercentChange'] = helper.util.getfloat(quote.pop('Percent Change'))
                quote['52WeekHigh'] = helper.util.getfloat(quote.pop('52 Week High'))
                quote['52WeekLow'] = helper.util.getfloat(quote.pop('52 Week Low'))
                quote['Ticker'] = cboe_ticker
                quote['SravzId'] = settings.constants.ST_LOUIS_FRED_VIX_MAP[ticker]
                quote['Name'] = settings.constants.ST_LOUIS_FRED_VIX_MAP[ticker]
                data = we.get_data_from_html_table_ignore_missing_tags(tables[1]) + we.get_data_from_html_table_ignore_missing_tags(tables[1])
                for item in data:
                    quote[item[0]] = item[1]
                # Rename columns
                quote['PreviousClose'] = quote.pop('Previous Close')
                quotes.append(quote)
            except:
                self.logger.error(
                    'Failed to process quote {0}'.format(ticker), exc_info=True)
        if upload_to_db and quotes:
            self.upload_quotes_to_db(quotes, collection_name='quotes_vix')

    def get_historical_vix_quotes(self, tickers=[], upload_to_db=False, from_date=None, ndays_back=None):
        '''
            Uploads vix quotes
        '''
        tickers = tickers or settings.constants.ST_LOUIS_FRED_VIX_MAP.keys()
        for ticker in tickers:
            try:
                self.logger.info("Processing quote: {0}".format(ticker))
                fred = Fred(api_key=settings.constants.ST_LOUIS_FRED_API_KEY)
                data = fred.get_series(ticker)
                if from_date:
                    data = data.loc[from_date:]
                if ndays_back:
                    data = data.loc[helper.util.get_n_days_back_date(
                        ndays_back):]
                quotes = []
                for key in data.keys():
                    quote = {}
                    quote['Date'] = key
                    quote['Last'] = helper.util.getfloat(data[key])
                    quotes.append(quote)
                if upload_to_db:
                    self.awse.upload_quotes_to_s3(quotes, settings.constants.ST_LOUIS_FRED_VIX_MAP[ticker])
                    # self.upload_quotes_to_db(
                    #     quotes, collection_name=settings.constants.ST_LOUIS_FRED_VIX_MAP[
                    #         ticker],
                    #     db_type='historical', ndays_back=ndays_back)
            except Exception:
                self.logger.error(
                    'Failed to process quote {0}'.format(ticker), exc_info=True)

    def upload_quotes_to_db(self, data, collection_name, db_type='live', ndays_back = None):
        if db_type == 'live':
            mdbe = mdb.engine()
            quotes_stocks_col = mdbe.get_collection(collection_name)
            for item in data:
                item['Time'] = datetime.datetime.now(datetime.UTC)
                quotes_stocks_col.update_one({"SravzId": item['SravzId']}, {
                    "$set": item}, upsert=True)
        elif db_type == 'historical':
            mdbe_historical = mdb.engine(
                database_name='historical', database_url='historical_url')
            quotes_col = mdbe_historical.get_collection(collection_name)
            for item in data:
                if ndays_back and (datetime.datetime.now() - item['Date']).days > ndays_back:
                    continue
                quotes_col.update_one({"Date": item['Date']}, {
                    "$set": item}, upsert=True)
