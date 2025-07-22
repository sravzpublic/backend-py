#!/usr/bin/env python
import json, datetime, pycountry
from src.services import mdb
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings

def upload_assets():
    mdbe = mdb.engine()
    eode = eodhistoricaldata.engine()
    futures_assets = []
    for future_asset in eode.get_futures_symbols():
        country = pycountry.countries.get(name=future_asset['Country'])
        if not country:
            country = pycountry.countries.get(alpha_2=future_asset['Country'])
        if not country:
            country = pycountry.countries.get(alpha_3=future_asset['Country'])
        if country:
            future_asset['SravzId'] = '{0}_{1}_{2}'.format("fut", country.alpha_2.lower(), future_asset['Code']).lower()
            future_asset['APICode'] = "{0}.{1}".format(future_asset.get('Code'), country.alpha_2.upper())
        else:
            future_asset['SravzId'] = '{0}_{1}_{2}'.format("fut", future_asset['Country'], future_asset['Code']).lower()
            future_asset['APICode'] = "{0}.{1}".format(future_asset.get('Code'), future_asset['Country'])
        future_asset["Ticker"] = future_asset["Code"]
        futures_assets.append(future_asset)

    mdbe.upsert_to_collection(settings.constants.FUTURE_ASSETS_COLLECTION, futures_assets)
    mdbe.create_index_collection(settings.constants.FUTURE_ASSETS_COLLECTION, "SravzId")



