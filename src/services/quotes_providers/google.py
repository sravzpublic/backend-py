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

import urllib.request, urllib.parse, urllib.error
import time
import datetime
from src.util import helper

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
            { 'symbol': self.symbol,
              'date'  : self.date[bar].strftime('%Y-%m-%d'),
              'time'  : self.time[bar].strftime('%H:%M:%S'),
              'open'  : self.open_[bar],
              'high'  : self.high[bar],
              'low'   : self.low[bar],
              'close' :self.close[bar],
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
            'http://www.google.com/finance/historical?q={0}'.format(self.symbol)
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
    print(q)  # print it out


            