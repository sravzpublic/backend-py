#!/usr/bin/python
import json
import urllib.request, urllib.parse, urllib.error, io
import pandas as pd
from src.util import helper, settings, logger
from src.services.quotes_providers import quote_data, yahoo
from src.services import webcrawler
from datetime import datetime

class engine(object):
    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.web_engine = webcrawler.engine()
        self.yahooe = yahoo.engine()
    """description of class"""
    def get_historical_price(self, tickers, source):
        tickers_result = []
        failed_tickers = []
        passed_tickers = []

        today_str = datetime.today().strftime('%Y-%m-%d').split('-')
        month_str = datetime.now().strftime("%b") # 'dec'
        year = today_str[0]
        month = today_str[1]
        day = today_str[2]

        for ticker in tickers:
            try:
                if source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_STOOQ:
                    url = "https://stooq.com/q/d/l/?s={0}.us&i=d".format(ticker)
                    csv = urllib.request.urlopen(url).read()
                    data = pd.read_csv(io.BytesIO(csv))
                    tickers_result.append({'ticker': ticker, 'data': data.to_dict('records')})
                elif source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_WSJ:
                    url = "http://quotes.wsj.com/{0}/historical-prices/download?MOD_VIEW=page&num_rows=6299.041666666667&range_days=6299.041666666667&startDate=09/06/2000&endDate={1}/{2}/{3}".format(ticker, month, day, year)
                    csv = urllib.request.urlopen(url).read()
                    data = pd.read_csv(io.BytesIO(csv))
                    data['Date'] = pd.to_datetime(data.Date)
                    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
                    tickers_result.append({'ticker': ticker, 'data': data.to_dict('records')})
                elif source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_INVESTOPEDIA:
                    url = "https://globalquotes.xignite.com/v3/xGlobalQuotes.json/GetChartBars?IdentifierType=Symbol&Identifier={0}&StartTime=5%2F14%2F1900+4%3A00+PM&EndTime={1}%2F{2}%2F{3}+4%3A00+PM&AdjustmentMethod=All&IncludeExtended=False&Precision=Hours&Period=24&_token=15B2186D55CB1AEFD12E7C2C2DE9CBB9110DFB516C5307188C5E44131653A7F1F21A023036EBFDEA31AFD7ABEE6327134A5B6FFB&_token_userid=46384".format(ticker, month, day, year)
                    json_data = urllib.request.urlopen(url).read()
                    raw_data = json.loads(json_data)['ChartBars']
                    data = []
                    for item in raw_data:
                        row = {}
                        trade_date = item.pop("StartDate").split('/')
                        row["Date"] = "{0}-{1}-{2}".format(trade_date[2], trade_date[0], trade_date[1])
                        for key in ["Volume","Close","Low","High","Open"]:
                            row[key] = item[key]
                        data.append(row)
                elif source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_MACROTRENDS:
                    url = "http://download.macrotrends.net/assets/php/stock_data_export.php?t={0}".format(ticker)
                    csv = urllib.request.urlopen(url).read()
                    # Remove disclaimer
                    csv = csv[csv.index(b"date,open,high,low,close,volume"):]
                    data = pd.read_csv(io.BytesIO(csv))
                    data = data.rename(index=str, columns={"date": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume" })
                    tickers_result.append({'ticker': ticker, 'data': data.to_dict('records')})
                elif source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_TIINGO:
                    url = "https://api.tiingo.com/tiingo/daily/{0}/prices?startDate=2012-1-1&endDate={1}-{2}-{3}&token=19d445c12978b1954b05cff11893c9bb295b60d1".format(ticker, year, month, day)
                    data = pd.read_json(url)
                    data['date'] = data['date'].dt.strftime('%Y-%m-%d')
                    data = data.rename(index=str, columns={"date": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume" })
                    tickers_result.append({'ticker': ticker, 'data': data.to_dict('records')})
                elif source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_ALPHA_ADVANTAGE:
                    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={0}&apikey={1}&datatype=csv&outputsize=full".format(ticker, settings.constants.ALPHA_ADVANTAGE_API_KEY)
                    csv = urllib.request.urlopen(url).read()
                    #csv = csv[csv.index(b"timestamp,open,high,low,close,volume"):]
                    data = pd.read_csv(io.BytesIO(csv))
                    data = data.rename(index=str, columns={"timestamp": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume" })
                    tickers_result.append({'ticker': ticker, 'data': data.to_dict('records')})
                elif source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_YAHOO:
                    url = 'yahoo_src'
                    data = self.yahooe.get_historical_quotes(ticker)
                    tickers_result.append({'ticker': ticker, 'data': data.to_dict('records')})
                elif source == settings.constants.HISTORICAL_QUOTE_DATA_SRC_CNBC:
                    url = "https://ts-api.cnbc.com/harmony/app/bars/{0}/1D/19021127000000/{1}{2}{3}000000/adjusted/EST5EDT.json".format(ticker, year, month, day)
                    json_data = urllib.request.urlopen(url).read()
                    raw_data = json.loads(json_data)
                    data = raw_data['barData']['priceBars']
                    for item in data:
                        trade_date = item.pop("tradeTime")
                        item["Date"] = "{0}-{1}-{2}".format(trade_date[:4], trade_date[4:6], trade_date[6:8])
                        item["Volume"] = item.pop("volume")
                        item["Open"] = item.pop("open")
                        item["High"] = item.pop("high")
                        item["Low"] = item.pop("low")
                        item["Close"] = item.pop("close")
                    self.logger.info("Data Rows for ticker:{0} {1} - {2}".format(ticker,url,len(data)))
                elif source == settings.constants.EODHISTORICALDATA:
                    url = "https://eodhistoricaldata.com/api/real-time/{0}.US?api_token={1}&fmt=json".format(ticker, settings.constants.EODHISTORICALDATA_API_KEY2)
                    json_data = urllib.request.urlopen(url).read()
                    ticker  = json.loads(json_data)
                    ticker ["Time"] = datetime.fromtimestamp(ticker.pop("timestamp"))
                    ticker ["Code"] = ticker.pop("code")
                    ticker ["Volume"] = ticker.pop("volume")
                    ticker ["Open"] = ticker.pop("open")
                    ticker ["High"] = ticker.pop("high")
                    ticker ["Low"] = ticker.pop("low")
                    ticker ["Close"] = ticker.pop("close")
                    ticker ["PreviousClose"] = ticker.pop("previousClose")
                    ticker ["Change"] = ticker.pop("change")
                    ticker ["PercentChange"] = ticker.pop("change_p")
                    tickers_result.append(ticker)
                passed_tickers.append(ticker)
            except:
                self.logger.error('Failed to process quote: {0} - {1}'.format(ticker, url), exc_info=True)
                failed_tickers.append(ticker)
        return quote_data.QuotaData(passed_tickers, failed_tickers, tickers_result)
