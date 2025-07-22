#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011, Mark Chenoweth
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import urllib.request
import urllib.parse
import urllib.error
import time
import datetime
import requests
import re
import io
from src.util import settings, logger, helper
from src.services import webcrawler
from bs4 import BeautifulSoup
from time import mktime
import pandas as pd


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()
        self.INDEX_OF_INTEREST = ['EURONEXT', 'BEL', 'MOEX', 'NZX',
                                  'TSEC', 'TSX', 'IBOVESPA', 'IPC', 'CLX IPSA', 'MERVAL',
                                  'ORDINARIES']
        self.INDEX_COUNTRY = {
            'EURONEXT': 'EU',
            'BEL': 'EU',
            # 'MOEX': 'RU',
            # 'ORDINARIES' : 'AU',
            'NZX': 'NZ',
            'TSEC': 'CA',
            'TSX': 'CA',
            'IBOVESPA': 'BR',
            'IPC': 'MX',
            'CLX IPSA': 'CL',
            'MERVAL': 'RU'
        }

    """description of class"""

    def get_world_index_quotes(self):
        url = 'https://finance.yahoo.com/world-indices/'
        data = self.we.get_data_from_html_table(
            None, 'yfinlist-table W(100%) BdB Bdc($tableBorderGray)', url=url)
        quotes = []
        for item in data:
            quote = {}
            if not any([index.lower() in item['Name'].lower() for index in self.INDEX_OF_INTEREST]):
                continue
            quote['Name'] = item['Name']
            quote['Ticker'] = item['Symbol'].replace('^', ' ').lower()
            try:
                quote['Country'] = [self.INDEX_COUNTRY[key]
                                    for key in self.INDEX_COUNTRY if key.lower() in item['Name'].lower()].pop()
            except:
                continue
            quote['SravzId'] = "idx_%s_%s" % (
                quote['Country'].lower(), quote['Ticker'].lower())
            quote['Change'] = helper.util.getfloat(item.pop('Change')[0])
            quote['PercentChange'] = item.pop('%Change')
            quote['Last'] = helper.util.getfloat(item.pop('LastPrice'))
            quotes.append(quote)
        return quotes

    def _get_crumbs_and_cookies(self, stock):
        """
        get crumb and cookies for historical data csv download from yahoo finance

        parameters: stock - short-handle identifier of the company

        returns a tuple of header, crumb and cookie
        """

        url = 'https://finance.yahoo.com/quote/{}/history'.format(stock)
        with requests.session():
            header = {'Connection': 'keep-alive',
                      'Expires': '-1',
                      'Upgrade-Insecure-Requests': '1',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                      }

            website = requests.get(url, headers=header)
            soup = BeautifulSoup(website.text, 'lxml')
            crumb = re.findall('"CrumbStore":{"crumb":"(.+?)"}', str(soup))

            return (header, crumb[0], website.cookies)

    def convert_to_unix(self, date):
        """
        converts date to unix timestamp

        parameters: date - in format (dd-mm-yyyy)

        returns integer unix timestamp
        """
        datum = datetime.datetime.strptime(date, '%d-%m-%Y')

        return int(mktime(datum.timetuple()))

    def get_quote_in_csv(self, stock, interval='1d', day_begin='01-01-1990', day_end=None):
        """
        queries yahoo finance api to receive historical data in csv file format

        parameters:
            stock - short-handle identifier of the company

            interval - 1d, 1wk, 1mo - daily, weekly monthly data

            day_begin - starting date for the historical data (format: dd-mm-yyyy)

            day_end - final date of the data (format: dd-mm-yyyy)

        returns a list of comma seperated value lines
        """
        day_end = day_end or datetime.datetime.today().strftime('%d-%m-%Y')
        day_begin_unix = self.convert_to_unix(day_begin)
        day_end_unix = self.convert_to_unix(day_end)

        header, crumb, cookies = self._get_crumbs_and_cookies(stock)

        with requests.session():
            url = 'https://query1.finance.yahoo.com/v7/finance/download/' \
                '{stock}?period1={day_begin}&period2={day_end}&interval={interval}&events=history&crumb={crumb}' \
                .format(stock=stock, day_begin=day_begin_unix, day_end=day_end_unix, interval=interval, crumb=crumb)

            website = requests.get(url, headers=header, cookies=cookies)

            return website.text

    def get_historical_quotes(self, ticker):
        csv = self.get_quote_in_csv(ticker, interval='1d').encode()
        data = pd.read_csv(io.BytesIO(csv))
        return data


class Quote(object):

    DATE_FMT = '%Y-%m-%d'
    TIME_FMT = '%H:%M:%S'

    def __init__(self):
        self.symbol = ''
        (
            self.date,
            self.time,
            self.open_,
            self.high,
            self.low,
            self.close,
            self.volume,
        ) = ([] for _ in range(7))

    def append(
        self,
        dt,
        open_,
        high,
        low,
        close,
        volume,
    ):

        self.date.append(dt.date())
        self.time.append(dt.time())
        self.open_.append(helper.util.getfloat(open_))
        self.high.append(helper.util.getfloat(high))
        self.low.append(helper.util.getfloat(low))
        self.close.append(helper.util.getfloat(close))
        self.volume.append(helper.util.getint(volume))

    def to_dicts(self):
        return [
            {'symbol': self.symbol,
             'date': self.date[bar].strftime('%Y-%m-%d'),
             'time': self.time[bar].strftime('%H:%M:%S'),
             'open': self.open_[bar],
             'high': self.high[bar],
             'low': self.low[bar],
             'close':self.close[bar],
             'volume': self.volume[bar],
             } for bar in range(len(self.close))]

    def to_csv(self):
        return ''.join(['{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n'.format(
            self.symbol,
            self.date[bar].strftime('%Y-%m-%d'),
            self.time[bar].strftime('%H:%M:%S'),
            self.open_[bar],
            self.high[bar],
            self.low[bar],
            self.close[bar],
            self.volume[bar],
        ) for bar in range(len(self.close))])

    def write_csv(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_csv())

    def read_csv(self, filename):
        self.symbol = ''
        (
            self.date,
            self.time,
            self.open_,
            self.high,
            self.low,
            self.close,
            self.volume,
        ) = ([] for _ in range(7))
        for line in open(filename, 'r'):
            (
                symbol,
                ds,
                ts,
                open_,
                high,
                low,
                close,
                volume,
            ) = line.rstrip().split(',')
            self.symbol = symbol
            dt = datetime.datetime.strptime(ds + ' ' + ts,
                                            self.DATE_FMT + ' ' + self.TIME_FMT)
            self.append(
                dt,
                open_,
                high,
                low,
                close,
                volume,
            )
        return True

    def __repr__(self):
        return self.to_csv()


class GoogleQuote(Quote):

    ''' Daily quotes from Google. Date format='yyyy-mm-dd' '''

    def __init__(
        self,
        symbol,
        start_date,
        end_date=datetime.date.today().isoformat(),
    ):
        super(GoogleQuote, self).__init__()
        self.symbol = symbol.upper()
        start = datetime.date(helper.util.getint(start_date[0:4]),
                              helper.util.getint(start_date[5:7]),
                              helper.util.getint(start_date[8:10]))
        end = datetime.date(helper.util.getint(end_date[0:4]), helper.util.getint(end_date[5:7]),
                            helper.util.getint(end_date[8:10]))
        url_string = \
            'http://www.google.com/finance/historical?q={0}'.format(
                self.symbol)
        url_string += \
            '&startdate={0}&enddate={1}&output=csv'.format(start.strftime('%b %d, %Y'
                                                                          ), end.strftime('%b %d, %Y'))
        csv = urllib.request.urlopen(url_string).readlines()
        csv.reverse()
        for bar in range(0, len(csv) - 1):
            (
                ds,
                open_,
                high,
                low,
                close,
                volume,
            ) = csv[bar].rstrip().split(',')
            (open_, high, low, close) = [helper.util.getfloat(x) for x in [open_,
                                                                           high, low, close]]
            dt = datetime.datetime.strptime(ds, '%d-%b-%y')
            self.append(
                dt,
                open_,
                high,
                low,
                close,
                volume,
            )


if __name__ == '__main__':
    q = GoogleQuote('aapl', '1987-01-01')  # download year to date Apple data
    # https://query1.finance.yahoo.com/v7/finance/download/GOOG?period1=1529853988&period2=1532445988&interval=1d&events=history&crumb=BTp0fPNsl9u
    print(q)  # print it out
