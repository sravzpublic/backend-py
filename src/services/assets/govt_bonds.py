#!/usr/bin/env python
import json, datetime, pycountry
from src.services import mdb
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings

def upload_assets():
    mdbe = mdb.engine()
    eode = eodhistoricaldata.engine()
    gbond_assets = []
    for gbond_asset in eode.get_list_of_govt_bonds():
        gbond_asset["SravzId"] = "gbond_{0}".format(gbond_asset["Code"]).lower().replace('-','_')
        gbond_asset["Ticker"] = gbond_asset["Code"]
        gbond_assets.append(gbond_asset)
    mdbe.upsert_to_collection(settings.constants.GBOND_ASSETS_COLLECTION, gbond_assets)
    mdbe.create_index_collection(settings.constants.GBOND_ASSETS_COLLECTION, "SravzId")



