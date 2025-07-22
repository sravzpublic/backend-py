#!/usr/bin/env python
import json, datetime, pycountry
from src.services import mdb
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings

##### Need to register for fundamental data...TODO
def upload_assets():
    pass
    # mdbe = mdb.engine()
    # eode = eodhistoricaldata.engine()
    # crypto_assets = []
    # for crypto_asset in eode.get_list_of_crypto():
    #     crypto_asset["SravzId"] = "crypto_{0}".format(crypto_asset["Code"]).lower().replace('-','_')
    #     crypto_asset["Ticker"] = crypto_asset["Code"]
    #     crypto_assets.append(crypto_asset)
    # mdbe.upsert_to_collection(settings.constants.CRYPTO_ASSETS_COLLECTION, crypto_assets)
    # mdbe.create_index_collection(settings.constants.CRYPTO_ASSETS_COLLECTION, "SravzId")
