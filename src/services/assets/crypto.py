#!/usr/bin/env python
import json, datetime, pycountry
from src.services import mdb
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings

def upload_assets():
    mdbe = mdb.engine()
    eode = eodhistoricaldata.engine()
    crypto_assets = []
    for crypto_asset in eode.get_list_of_crypto():
        crypto_asset["SravzId"] = "crypto_{0}".format(crypto_asset["Code"]).lower().replace('-','_')
        crypto_asset["Ticker"] = crypto_asset["Code"]
        if crypto_asset["SravzId"] in ['crypto_btc_usd', 'crypto_eth_usd', 'crypto_usdt_usd', 'crypto_bnb_usd', 'crypto_doge_usd']:
            crypto_assets.append(crypto_asset)
    mdbe.upsert_to_collection(settings.constants.CRYPTO_ASSETS_COLLECTION, crypto_assets)
    mdbe.create_index_collection(settings.constants.CRYPTO_ASSETS_COLLECTION, "SravzId")



