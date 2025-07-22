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
import json, urllib


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()
        self.awse = aws.engine()
        self.mdbe = mdb.engine()

    def get_rate_quotes(self, upload_to_db=False, db_type=settings.constants.DB_TYPE_LIVE):
        quotes = []
        url = 'https://www.global-rates.com/interest-rates/central-banks/central-banks.aspx'
        self.logger.info("processing %s" % (url))
        html_data = requests.get(url).text
        soup = BeautifulSoup(html_data, 'html.parser')
        for item in soup.find_all("tr"):
            try:
                if item.find_all("td")[1].text == 'Europe':
                        quote = {}
                        self.logger.info("processing country %s" % (item.find_all("td")[1].text))
                        quote['SravzId'] = "int_ecb_eur"
                        quote['Last'] = helper.util.getfloat(self.we.sanitize(item.find_all("td")[2].text))
                        quote['Name'] = item.find_all("td")[0].text
                        quote['Country'] = "Europe"
                        quote['RevisedDate'] = self.we.sanitize(item.find_all("td")[5].text)
                        quotes.append(quote)
                elif item.find_all("td")[1].text == 'Great Britain':
                        quote = {}
                        self.logger.info("processing country %s" % (item.find_all("td")[1].text))
                        quote['SravzId'] = "int_gbr_gbp"
                        quote['Last'] = helper.util.getfloat(self.we.sanitize(item.find_all("td")[2].text))
                        quote['Name'] = item.find_all("td")[0].text
                        quote['Country'] = "GB"
                        quote['RevisedDate'] = self.we.sanitize(item.find_all("td")[5].text)
                        quotes.append(quote)
                else:
                    country = pycountry.countries.get(name=item.find_all("td")[1].text)
                    if country:
                        quote = {}
                        self.logger.info("processing country %s" % (item.find_all("td")[1].text))
                        quote['SravzId'] = "int_{0}_{1}".format(country.alpha_3.lower(),
                                                            country_currency_mapping.COUNTRY_CURRENCY_MAPPING.get(country.alpha_2)[0].lower())
                        quote['Last'] = helper.util.getfloat(self.we.sanitize(item.find_all("td")[2].text))
                        quote['Name'] = item.find_all("td")[0].text
                        quote['Country'] = country.alpha_2
                        quote['RevisedDate'] = self.we.sanitize(item.find_all("td")[5].text)
                        quotes.append(quote)
            except Exception:
                continue
        if upload_to_db and db_type == settings.constants.DB_TYPE_LIVE:
            self.upload_quotes_to_db(quotes, collection_name='quotes_rates',
                                     db_type=db_type)


    def get_historical_mortgage_rates_quotes(self, tickers=[], upload_to_db=False, from_date=None, ndays_back=None):
        '''
            Uploads rates data to mongodb
        '''
        tickers = tickers or settings.constants.ST_LOUIS_FRED_MORTGAGE_RATES_MAP.keys()
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
                    self.awse.upload_quotes_to_s3(quotes, settings.constants.ST_LOUIS_FRED_MORTGAGE_RATES_MAP[ticker])
                    # self.upload_quotes_to_db(
                    #     quotes, collection_name=settings.constants.ST_LOUIS_FRED_MORTGAGE_RATES_MAP[
                    #         ticker],
                    #     db_type='historical', ndays_back=ndays_back)
            except Exception:
                self.logger.error(
                    'Failed to process quote {0}'.format(ticker), exc_info=True)

    def _update_mortgage_rates_format(self, input_quotes, ticker_col_lambda):
        quotes = []
        for _item in itertools.chain(input_quotes):
            for item in _item:
                new_item = {}
                for key in item.keys():
                    _key = re.sub(r'[^\x00-\x7F]+','', key).split('\n', 1)[0]
                    _key = re.sub(r'\W+', '', _key)
                    new_item[_key] = item.get(key)
                new_item['Source'] = 'DCU'
                new_item['Country'] = 'US'
                # self.logger.info("New item {0}".format(new_item))
                ticker_col = None
                if 'Terms' in new_item:
                    ticker_col = 'Terms'
                elif 'ARMProgram' in new_item:
                    ticker_col = 'ARMProgram'
                if ticker_col:
                    new_item['SravzId'] = re.sub(r'[^\x00-\x7F]+','', ticker_col_lambda(new_item, ticker_col))
                    quotes.append(new_item)
                else:
                    self.logger.error('Ticker columns could not be determined in {0}'.format(new_item), exc_info=True)
        return quotes

    def get_mortgage_rates_quotes(self, upload_to_db=False):
        '''
            Uploads mortgage rates data to mongodb
        '''
        try:
            self.logger.info("Processing DCU variable rates")
            _dcu_variable_rates_data = []
            for table_data in self.we.get_html_tables(None, url='https://www.dcu.org/borrow/mortgage-loans/buy-a-home.html')[4:8]:
                _dcu_variable_rates_data.append(self.we.get_data_from_html_table_ignore_missing_tags(table_data,
                first_row_is_header_row = True))
            self.logger.info("DCU variable rates obtained: {0}".format(_dcu_variable_rates_data))
            dcu_variable_rates_data = self._update_mortgage_rates_format(_dcu_variable_rates_data, lambda item, key: 'int_usa_usd_dcu_variable_%s'%(item[key]))
        except Exception:
            self.logger.error('Failed to upload variable rates', exc_info=True)

        try:
            self.logger.info("Processing DCU fixed rates")
            _dcu_fixed_rates_data = []
            for table_data in self.we.get_html_tables(None, url='https://www.dcu.org/borrow/mortgage-loans/buy-a-home.html')[0:4]:
                _dcu_fixed_rates_data.append(self.we.get_data_from_html_table_ignore_missing_tags(table_data,
                first_row_is_header_row = True))
            self.logger.info("DCU fixed rates obtained: {0}".format(_dcu_fixed_rates_data))
            dcu_fixed_rates_data = self._update_mortgage_rates_format(_dcu_fixed_rates_data, lambda item, key: 'int_usa_usd_dcu_variable_%s'%(item[key]))
        except Exception:
            self.logger.error('Failed to upload fixed rates', exc_info=True)

        quotes = dcu_variable_rates_data + dcu_fixed_rates_data
        if upload_to_db:
            self.upload_quotes_to_db(quotes, collection_name='quotes_mortgage')
        return quotes



    def get_historical_rates_quotes(self, tickers=[], upload_to_db=False, from_date=None, ndays_back=None):
        '''
            Uploads rates data to mongodb
        '''
        tickers = tickers or settings.constants.ST_LOUIS_FRED_INTEREST_RATES_MAP.keys()
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
                    self.awse.upload_quotes_to_s3(quotes, settings.constants.ST_LOUIS_FRED_INTEREST_RATES_MAP[ticker])
                    # self.upload_quotes_to_db(
                    #     quotes, collection_name=settings.constants.ST_LOUIS_FRED_INTEREST_RATES_MAP[
                    #         ticker],
                    #     db_type='historical', ndays_back=ndays_back)
            except Exception:
                self.logger.error(
                    'Failed to process quote {0}'.format(ticker), exc_info=True)

        try:
            url = 'https://www.bcb.gov.br/api/conteudo/pt-br/INTEREST/'
            data = self.we.get_data_from_url(url, return_type="json")
            quotes = []
            for item in data['conteudo']:
                quote = {}
                try:
                    quote['Date'] = datetime.datetime.strptime(item['DataReuniaoCopom'][:10], '%Y-%m-%d')
                    quote['Last'] = helper.util.getfloat(item['MetaSelic'])
                except Exception:
                    continue
                quotes.append(quote)
            if upload_to_db:
                self.awse.upload_quotes_to_s3(quotes, 'int_bra_brl')
                # self.upload_quotes_to_db(
                #     quotes, collection_name='int_bra_brl', db_type='historical', ndays_back=ndays_back)
        except Exception:
            self.logger.error(
                'Failed to process quote {0}'.format('int_bra_brl'), exc_info=True)


        try:
            url = 'https://www.rba.gov.au/statistics/cash-rate/#cash-rate-chart'
            data = self.we.get_data_from_html_table(None, None, url=url, table_attrs={"id": "datatable"})
            quotes = []
            for item in data:
                quote = {}
                quote['Date'] = datetime.datetime.strptime(item['EffectiveDate'], '%d %b %Y')
                quote['Last'] = helper.util.getfloat(item['Cashratetarget%'])
                quotes.append(quote)
            if upload_to_db:
                self.awse.upload_quotes_to_s3(quotes, 'int_aus_aud')
            # if upload_to_db:
            #     self.upload_quotes_to_db(
            #         quotes, collection_name='int_aus_aud', db_type='historical', ndays_back=ndays_back)
        except Exception:
            self.logger.error(
                'Failed to process quote {0}'.format('int_aus_aud'), exc_info=True)

        try:
            url = 'https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?Travel=NIxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FD=1&FM=Jan&FY=2009&TD={0}&TM={1}&TY={2}&FNY=&CSVF=TT&html.x=277&html.y=32&C=13T&Filter=N#'.format(
                datetime.datetime.now().day, datetime.datetime.now().strftime("%B"), datetime.datetime.now().year)
            data = self.we.get_data_from_html_table(None, None, url=url, table_attrs={"id": "stats-table"})
            quotes = []
            for item in data:
                quote = {}
                quote['Date'] = datetime.datetime.strptime(item['Date'], '%d %b %y')
                quote['Last'] = helper.util.getfloat(item['OfficialBankRate\n[a][b]\nIUDBEDR'])
                quotes.append(quote)
            if upload_to_db:
                self.awse.upload_quotes_to_s3(quotes, 'int_gbr_gbp')
            # if upload_to_db:
            #     self.upload_quotes_to_db(
            #         quotes, collection_name='int_gbr_gbp', db_type='historical', ndays_back=ndays_back)
        except Exception:
            self.logger.error(
                'Failed to process quote {0}'.format('int_gbr_gbp'), exc_info=True)

        # try:
        #     url = 'https://www.bankofcanada.ca/rates/interest-rates/canadian-interest-rates/?lookupPage=lookup_canadian_interest.php&startRange=2000-05-31&rangeType=dates&dFrom=2009-06-01&dTo={0}&rangeValue=1&rangeWeeklyValue=1&rangeMonthlyValue=1&ByDate_frequency=daily&submit_button=Submit'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
        #     data = self.we.get_data_from_html_table(None, 'bocss-table bocss-table--hoverable bocss-table--alternating bocss-table--40-width rates series', url=url)
        #     quotes = []
        #     for item in data:
        #         quote = {}
        #         quote['Date'] = datetime.datetime.strptime(item['Date'], '%Y-%m-%d')
        #         quote['Last'] = helper.util.getfloat(item['V39079'])
        #         quotes.append(quote)
        #     if upload_to_db:
        #         self.awse.upload_quotes_to_s3(quotes, 'int_can_cad')
        #     # if upload_to_db:
        #     #     self.upload_quotes_to_db(
        #     #         quotes, collection_name='int_can_cad', db_type='historical', ndays_back=ndays_back)
        # except Exception:
        #     self.logger.error(
        #         'Failed to process quote {0}'.format('int_can_cad'), exc_info=True)

        try:
            url = 'https://www.quandl.com/api/v3/datasets/BCB/17899.json?api_key=My4TXrS2R1VeXt-shsYD'
            data = self.we.get_data_from_url(url, return_type="json")
            quotes = []
            for item in data['dataset']['data']:
                quote = {}
                quote['Date'] = datetime.datetime.strptime(item[0], '%Y-%m-%d')
                quote['Last'] = helper.util.getfloat(item[1])
                quotes.append(quote)
            if upload_to_db:
                self.awse.upload_quotes_to_s3(quotes, 'int_chn_cny')
            # if upload_to_db:
            #     self.upload_quotes_to_db(
            #         quotes, collection_name='int_chn_cny', db_type='historical', ndays_back=ndays_back)
        except Exception:
            self.logger.error(
                'Failed to process quote {0}'.format('int_chn_cny'), exc_info=True)

        # try:
        #     url = 'https://sdw.ecb.europa.eu/browseTable.do?node=9691107'
        #     html_data = requests.get(url).text
        #     soup = BeautifulSoup(html_data, 'html.parser')
        #     quotes = []
        #     for item in soup.find_all("tr")[15:]:
        #         quote = {}
        #         quote['Date'] = datetime.datetime.strptime(
        #             item.find_all("td")[0].text, '%Y-%m-%d')
        #         quote['Last'] = helper.util.getfloat(
        #             item.find_all("td")[-1].text)
        #         quotes.append(quote)
        #     self.process_ticker('int_ecb_eur', quotes,
        #                         upload_to_db=upload_to_db, ndays_back=ndays_back)
        # except Exception:
        #     self.logger.error(
        #         'Failed to process quote {0}'.format('int_ecb_eur'), exc_info=True)

        # Upload rest of the interest rates: https://www.global-rates.com/interest-rates/central-banks/central-banks.aspx


        tickers = self.mdbe.get_collection_items(settings.constants.GBOND_ASSETS_COLLECTION)
        for ticker in tickers:
            try:
                url = "https://eodhistoricaldata.com/api/eod/{0}.gbond?api_token={1}&order=d&fmt=json".format(ticker['Code'], settings.constants.EODHISTORICALDATA_API_KEY2)
                self.logger.info("processing %s" % (url))
                json_data = urllib.request.urlopen(url).read()
                data  = json.loads(json_data)
                ticker.pop('_id')
                quotes = []
                for quote in data:
                    quote['Date'] = datetime.datetime.strptime(quote.pop('date'), '%Y-%m-%d')
                    quote["Volume"] = quote.pop("volume")
                    quote["Open"] = quote.pop("open")
                    quote["High"] = quote.pop("high")
                    quote["Low"] = quote.pop("low")
                    quote["Close"] = quote.pop("close")
                    quote["AdjustedClose"] = quote.pop("adjusted_close")
                    quotes.append(quote)
                if upload_to_db:
                    self.awse.upload_quotes_to_s3(quotes, ticker['SravzId'])
            except Exception:
                self.logger.error('Failed to process quote for ticker {0}'.format(ticker), exc_info=True)


    def process_ticker(self, ticker, quotes, upload_to_db=False, ndays_back=None):
        try:
            if upload_to_db:
                self.awse.upload_quotes_to_s3(quotes, ticker)
                # self.upload_quotes_to_db(
                #     quotes, collection_name=ticker, db_type='historical', ndays_back=ndays_back)
        except Exception:
            self.logger.error(
                'Failed to upload quote {0}'.format(ticker), exc_info=True)

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
