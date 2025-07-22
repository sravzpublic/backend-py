from src.util import settings, logger, helper
from src.services import webcrawler
from src.services import mdb
from bs4 import BeautifulSoup
import re, datetime, pymongo, sys, traceback
from itertools import islice
from random import shuffle
import pycountry

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()

    """description of class"""
    def get_quotes(self, tickers = []):
        '''
            e = engine()
            e.get_quotes_from_marketwatch(tickers = ['D'])
        '''
        tickers_result = []
        failed_tickers = []

        for ticker in tickers:
            try:
                url = 'http://www.marketwatch.com/investing/stock/%s'%(ticker)
                self.logger.info("processing %s"%(url))
                data = self.we.get_data_from_url(url)
                soup = BeautifulSoup(data, 'html.parser')
                bgName = self.we.sanitize(soup.find("h1", { "class" : "company__name" }).text)
                bgExchangeName = self.we.sanitize(soup.find("span", { "class" : "company__ticker" }).text)
                try:
                    # Market might be closed
                    bgLast = helper.util.getfloat(self.we.sanitize(soup.findAll("bg-quote", { "field" : "Last" })[0].string))
                except:
                    bgLast = helper.util.getfloat(self.we.sanitize(soup.findAll("span", { "class" : "value" })[0].string))
                bgChange = helper.util.getfloat(self.we.sanitize(soup.findAll("bg-quote", { "field" : "change" })[0].string))
                bgPercentChange = self.we.sanitize(soup.findAll("bg-quote", { "field" : "percentchange" })[0].string)
                bgPreviousClose = helper.util.getfloat(self.we.sanitize(soup.findAll("td", { "class" : "table__cell u-semi" })[0].string))
                bgPreviousChange = None
                bgPercentPreviousChange = None
                bgDayLow = helper.util.getfloat(self.we.sanitize(soup.findAll("span", { "class" : "low" })[0].text))
                bgDayHigh = helper.util.getfloat(self.we.sanitize(soup.findAll("span", { "class" : "high" })[0].text))
                bg52WeekLow = helper.util.getfloat(self.we.sanitize(soup.findAll("span", { "class" : "low" })[1].text))
                bg52WeekHigh = helper.util.getfloat(self.we.sanitize(soup.findAll("span", { "class" : "high" })[1].text))

                values = self.we.get_data_from_table_of_elements(url, "ul", "li", "small", "span", "list list--kv list--col50", "kv__item", "kv__label", "kv__value kv__primary ")
                values_dict = {}
                for entry in values:
                    values_dict.update(entry)

                bgDayOpen = helper.util.getfloat(values_dict.get("Open"))
                bgMarketCap = helper.util.getfloat(values_dict.get("MarketCap"))
                bgAvgVolume =  helper.util.getfloat(values_dict.get("AverageVolume"))
                bgPERatio =  helper.util.getfloat(values_dict.get("P/ERatio"))
                bgRevPerEmployee =  helper.util.getfloat(values_dict.get("Rev.perEmployee"))
                bgEPS =  helper.util.getfloat(values_dict.get("EPS"))
                bgDiv =  helper.util.getfloat(values_dict.get("Dividend"))
                bgDivYield =  helper.util.getfloat(values_dict.get("Yield"))
                bgExDivDate =  values_dict.get("Ex-DividendDate")


                tickers_result.append({'Ticker': ticker,
                    'Name': bgName,
                    'Exchange': bgExchangeName,
                    'Last': bgLast,
                    'Change': bgChange,
                    'PercentChange': bgPercentChange,
                    'PreviousClose': bgPreviousClose,
                    'PreviousChange': bgPreviousChange,
                    'PercentPreviousChange': bgPercentPreviousChange,
                    'DayOpen': bgDayOpen,
                    'DayLow': bgDayLow,
                    'DayHigh': bgDayHigh,
                    '52WeekLow': bg52WeekLow,
                    '52WeekHigh': bg52WeekHigh,
                    'MarketCap': bgMarketCap,
                    'AvgVolume': bgAvgVolume,
                    'PERatio': bgPERatio,
                    'RevPerEmployee': bgRevPerEmployee,
                    'EPS': bgEPS,
                    'Div': bgDiv,
                    'DivYield': bgDivYield,
                    'ExDivDate': bgExDivDate,
                    })
            except:
                self.logger.error('Failed to process quote', exc_info=True)
                failed_tickers.append(ticker)
        return (failed_tickers, tickers_result)

    def get_world_index_quotes(self):
        url = 'https://www.marketwatch.com/tools/stockresearch/globalmarkets/intIndices.asp'
        data = self.we.get_data_from_html_table(None, None, url=url)
        quotes = []
        for item in data:
            quote = {}
            quote['Ticker'] = item.pop('Symbol').replace(':', '_').lower()
            quote['SravzId'] = "idx_%s"%(quote['Ticker'].lower())
            quote['Name'] = item.pop('Company')
            if 'dow' in quote['Name'].lower():
                continue
            try:
                quote['Country'] = pycountry.countries.lookup(item.get('Country')).alpha_2
            except:
                continue
            quote['Change'] =  helper.util.getfloat(item.pop('Chg.'))
            quote['PercentChange'] = item.pop('%Chg.')
            quote['Last'] = helper.util.getfloat(item.pop('Last'))
            quotes.append(quote)
        return quotes

