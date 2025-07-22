#!/usr/bin/env python
import json, datetime
from src.services import mdb
from src.services.assets import sravz_assets, indices, crypto, forex, exchanges, govt_bonds, futures, bond
from src.util import settings, logger

def upload():
    _logger = logger.RotatingLogger(__name__).getLogger()

    try:
        indices.upload_assets()
    except Exception:
        _logger.error('Could not upload index assets to db', exc_info=True)

    _logger.info('Uploaded Index Assets')

    try:
        crypto.upload_assets()
    except Exception:
        _logger.error('Could not upload crypto assets to db', exc_info=True)

    _logger.info('Uploaded Crypto Assets')

    try:
        forex.upload_assets()
    except Exception:
        _logger.error('Could not upload forex assets to db', exc_info=True)

    _logger.info('Uploaded Forex Assets')

    try:
        exchanges.upload_assets()
    except Exception:
        _logger.error('Could not upload exchange assets to db', exc_info=True)

    _logger.info('Uploaded Exchange Assets')

    try:
        exchanges.upload_etfs_list()
    except Exception:
        _logger.error('Could not upload etf assets to db', exc_info=True)

    _logger.info('Uploaded ETF Assets')

    try:
        exchanges.upload_futures_list_to_mdb
    except Exception:
        _logger.error('Could not upload futures assets to db', exc_info=True)

    _logger.info('Uploaded Futures Assets')

    try:
        govt_bonds.upload_assets()
    except Exception:
        _logger.error('Could not upload govt_bond assets to db', exc_info=True)

    _logger.info('Uploaded govt bonds Assets')


    try:
        futures.upload_assets()
    except Exception:
        _logger.error('Could not upload futures assets to db', exc_info=True)

    _logger.info('Uploaded futures Assets')

    try:
        bond.upload_assets()
    except Exception:
        _logger.error('Could not upload bond assets to db', exc_info=True)

    _logger.info('Uploaded bond Assets')

    try:
        sravz_assets.upload_assets()
    except Exception:
        _logger.error('Could not upload sravz assets to db', exc_info=True)

    _logger.info('Uploaded Sravz Assets')
