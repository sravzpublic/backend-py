#!/usr/bin/env python
import json, datetime, pycountry
from src.services import mdb
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings

def upload_assets():
    mdbe = mdb.engine()
    eode = eodhistoricaldata.engine()
    bond_assets = []
    for bond_asset in eode.get_bond_symbols():
        country = pycountry.countries.get(name=bond_asset['Country'])
        if not country:
            country = pycountry.countries.get(alpha_2=bond_asset['Country'])
        if not country:
            country = pycountry.countries.get(alpha_3=bond_asset['Country'])
        if country:
            bond_asset['SravzId'] = '{0}_{1}_{2}'.format("bond", country.alpha_2.lower(), bond_asset['Code']).lower()
            bond_asset['APICode'] = "{0}.{1}".format(bond_asset.get('Code'), country.alpha_2.upper())
        else:
            bond_asset['SravzId'] = '{0}_{1}_{2}'.format("bond", bond_asset['Country'], bond_asset['Code']).lower()
            bond_asset['APICode'] = "{0}.{1}".format(bond_asset.get('Code'), bond_asset['Country'])
        bond_asset["Ticker"] = bond_asset["Code"]
        bond_assets.append(bond_asset)

    mdbe.upsert_to_collection(settings.constants.BOND_ASSETS_COLLECTION, bond_assets)
    mdbe.create_index_collection(settings.constants.BOND_ASSETS_COLLECTION, "SravzId")



