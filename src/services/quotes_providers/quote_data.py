#!/usr/bin/python
import urllib.request, urllib.parse, urllib.error, io
import pandas as pd
from src.util import helper
from src.util import logger

class QuotaData(object):
    def __init__(self, passed_tickers = [], failed_tickers = [], ticker_results = []):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.tickers_result = ticker_results
        self.failed_tickers = failed_tickers
        self.passed_tickers = passed_tickers
