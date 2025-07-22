import  requests, datetime, json
import pandas as pd
from src.util import settings
from src.services import webcrawler
from src.services import mdb

class engine(object):
    """description of class"""
    def get_unique_id(self, asset_type, asset_details):
        if asset_type == 'Future':
            month = 'NA'
            year = 'NA'
            currency = None
            exchange = None
            if asset_details["Country"] == "USA":
                currency = "usd"
                exchange = "cme"
            else:
                currency = "usd"
                exchange = "lme"
            month_year = asset_details["Month"].split(" ")
            if asset_details["Month"] and month_year:
                try:
                    month = month_year[0]
                    year = month_year[1] 
                except IndexError:
                    pass
            return "fut_%s_%s_%s_%s_%s"%(asset_details["Commodity"].replace(" ", "").replace("/", ""), month, year, currency, exchange)
