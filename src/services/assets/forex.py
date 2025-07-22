#!/usr/bin/env python
import json, datetime, pycountry
from src.services import mdb
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings

def upload_assets():
    mdbe = mdb.engine()
    eode = eodhistoricaldata.engine()
    forex_assets = []
    for forex_asset in eode.get_list_of_currencies():
        forex_asset["SravzId"] = "forex_{0}".format(forex_asset["Code"]).lower().replace('-','_')
        forex_asset["Ticker"] = forex_asset["Code"]
        forex_assets.append(forex_asset)
    mdbe.upsert_to_collection(settings.constants.FOREX_ASSETS_COLLECTION, forex_assets)
    mdbe.create_index_collection(settings.constants.FOREX_ASSETS_COLLECTION, "SravzId")



