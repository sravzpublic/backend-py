'''
Created on Jan 9, 2017

@author: admin
'''

from src.util import settings, helper

class Util(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
    @staticmethod
    def get_hostorical_collection_name_from_sravz_id(sravz_id):
        '''
            pe = engine()
            pe.get_historical_price('fut_gold_feb_17_usd_lme')
            pe.get_historical_price('stk_us_ayi')
        '''
        sravz_id = sravz_id.replace('$','dollar')
        generic_sravz_id = helper.get_generic_sravz_id(sravz_id)
        return generic_sravz_id
        