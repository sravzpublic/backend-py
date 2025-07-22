from src.services import mdb, aws
from src.services.cache import Cache
from src.util import settings, helper
import pandas as pd
import json

class engine(object):

    def __init__(self):
        self.awse = aws.engine()

    """description of class"""
    def get_index_components(self, sravzid):
        '''
        '''
        collection_name = "%s_components"%(sravzid)
        cache_key = 'get_index_components_%s'%(collection_name)
        value = Cache.Instance().get(cache_key)
        if not value:
            mdbe = mdb.engine()
            value = mdbe.get_collection_items(collection_name, find_clause = {},
                                            exclude_clause = {'_id': False})
            Cache.Instance().add(cache_key, value)
        return value

    def get_index_components_df(self, sravzid):
        '''
        '''
        index_components = self.get_index_components(sravzid)
        data_df = pd.DataFrame(index_components)
        return helper.util.convert_columns_and_index_to_str(data_df)

    def get_index_components_grouped_by_sector_df(self, sravzid):
        '''
        '''
        cache_key = 'get_index_components_grouped_by_sector_df_%s'%(sravzid)
        value = Cache.Instance().get(cache_key)
        if (type(value) == pd.core.frame.DataFrame and value.empty) or (value is None):
            index_components_df = self.get_index_components_df(sravzid)
            value = index_components_df.groupby(['sector']).count()
            Cache.Instance().add(cache_key, value)
        return value

    def get_eod_index_components_grouped_by_sector_df(self, sravzid):
        '''
        '''
        cache_key = 'get_index_components_grouped_by_sector_df_%s'%(sravzid)
        value = Cache.Instance().get(cache_key)
        if (type(value) == pd.core.frame.DataFrame and value.empty) or (value is None):
            data = json.loads(self.awse.download_object(settings.constants.SRAVZ_DATA_S3_BUCKET,
            "{0}{1}".format(settings.constants.SRAVZ_DATA_EOD_INDEX_COMPONENTS_PREFIX, sravzid),
            gzip_data = True))
            if data['Components']:
                components_df = pd.DataFrame.from_dict(data['Components'], orient='index')
                value = components_df.groupby(['Sector']).count()
                Cache.Instance().add(cache_key, value)
            else:
                raise Exception("Index components not found for {0}".format(sravzid))
        return value