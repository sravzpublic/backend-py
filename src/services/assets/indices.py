#!/usr/bin/env python
import json, datetime, pycountry
from src.services import mdb, aws
from src.services.quotes_providers import eodhistoricaldata
from src.util import settings, logger
from src.services.cache import Cache
import pandas as pd

mdbe = mdb.engine()
eode = eodhistoricaldata.engine()
awse = aws.engine()
logger = logger.RotatingLogger(__name__).getLogger()

def upload_assets():
    index_assets = []
    for index_asset in eode.get_list_of_indexes():
        try:
            index_asset["SravzId"] = "idx_{0}_{1}".format(pycountry.countries.lookup(index_asset["Country"]).alpha_2, index_asset["Code"]).lower()
        except:
            index_asset["SravzId"] = "idx_{0}_{1}".format(index_asset["Country"], index_asset["Code"]).lower()
        index_asset["Ticker"] = index_asset["Code"]
        index_assets.append(index_asset)
    mdbe.upsert_to_collection(settings.constants.INDEX_ASSETS_COLLECTION, index_assets)
    mdbe.create_index_collection(settings.constants.INDEX_ASSETS_COLLECTION, "SravzId")

def upload_index_components_to_s3(index_assets = None):
    '''
        upload_index_components_to_s3(index_assets = [{'SravzId': 'idx_us_ndx', 'Code': 'NDX', 'Exchange': 'INDX'}])
    '''
    _index_assets = index_assets or mdbe.get_collection_items(settings.constants.INDEX_ASSETS_COLLECTION)
    for index_asset in _index_assets:
        try:        
            awse.upload_to_bucket(settings.constants.SRAVZ_DATA_S3_BUCKET,
            "{0}{1}".format(settings.constants.SRAVZ_DATA_EOD_INDEX_COMPONENTS_PREFIX, index_asset['SravzId']),
            json.dumps(eode.get_index_components(index_asset['Code'], index_asset['Exchange'])),
            expires=None, gzip_data=True)
        except Exception:
            logger.error("Could not upload exchange components to S3 for {0}".format(index_asset['SravzId']), exc_info=True)

def get_index_components_from_s3(sravzid):
    '''
        get_index_components_from_s3('idx_us_ndx')
    '''
    return awse.download_object(settings.constants.SRAVZ_DATA_S3_BUCKET,
        "{0}{1}".format(settings.constants.SRAVZ_DATA_EOD_INDEX_COMPONENTS_PREFIX,sravzid),gzip_data=True)

def upload_index_components_to_mdb():
    index_assets_components_collection = mdbe.get_collection(settings.constants.INDEX_ASSETS_COMPONENTS_COLLECTION)
    for index_asset in mdbe.get_collection_items(settings.constants.INDEX_ASSETS_COLLECTION):
        try:        
            cache_key = 'upload_index_components_to_mdb_%s'%(index_asset['SravzId'])
            value = Cache.Instance().get(cache_key)
            if (type(value) == pd.core.frame.DataFrame and value.empty) or (value is None):
                data = json.loads(awse.download_object(settings.constants.SRAVZ_DATA_S3_BUCKET,
                "{0}{1}".format(settings.constants.SRAVZ_DATA_EOD_INDEX_COMPONENTS_PREFIX,
                index_asset['SravzId']),
                gzip_data = True))
                if data and data.get('Components'):
                    for component in data['Components'].values():
                        component['SravzId'] = index_asset['SravzId']
                        index_assets_components_collection.update_one({"SravzId": component['SravzId'],
                        "Code": component["Code"]}, {"$set": component}, upsert=True)
                    value = data['Components']
                    Cache.Instance().add(cache_key, value)
                    logger.info("Index components {0} uploaded to mdb".format(index_asset['SravzId']))
                else:
                    logger.info("Index components not found for {0}".format(index_asset['SravzId']))
        except Exception:
            logger.error("Could not upload exchange components to S3 for {0}".format(index_asset['SravzId']), exc_info=True)

