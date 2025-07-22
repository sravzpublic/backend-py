from bson.objectid import ObjectId
from src.services import mdb
from src.util import logger, settings, helper
import requests, pymongo, datetime
import traceback

LOGGER = logger.RotatingLogger(__name__).getLogger()

class engine(object):
    """description of class"""
    def get_smartthings_data(self, token):
        payload = "{ \"Id\": 3, \"Name\": \"test3\" }"
        headers = {
            'host': "api.sravz.com",
            'accept': "application/json, text/plain, */*",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "en-US,en;q=0.8",
            'content-type': "application/json",
            'authorization': "Bearer %s"%(token),
            'cache-control': "no-cache",
            'postman-token': "7ffa75f5-6459-8209-0e69-6898299c60b5"
            }

        response = requests.request("GET", settings.constants.SMARTTHINGS_URL, 
        data=payload, headers=headers)

        return response.text


    def get_smarthings_data_for_users(self):
        '''
            from src.services.iot_helpers import smarthings_reader
            sre = smarthings_reader.engine() 
            sre.get_smarthings_data_for_users()
        '''
        mdb_engine = mdb.engine()        
        smarthings_collection = mdb_engine.get_collection('smarthings') 
        smarthings_collection_items = mdb_engine.get_collection_items('smarthings', 
        iterator = True)
        for smarthing in smarthings_collection_items:
            LOGGER.info("Processing smarthings for user %s"%(smarthing['user']))
            try:
                st_data = self.get_smartthings_data(smarthing['token']['access_token'])
                smarthings_collection.update({'_id': ObjectId(smarthing['_id'])}, 
                {
                    '$push': {
                        'data': {
                            'key': datetime.datetime.now(datetime.UTC),
                            'value': st_data
                            }
                    }
                }, 
                upsert = True)
            except Exception:
                LOGGER.error("Could not process smartthing for user: %s "%(smarthing['user']), 
                exc_info=True)
