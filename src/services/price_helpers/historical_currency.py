from src.util import settings
from src.services import webcrawler

class engine_currency(object):
    """description of class"""
    def get_historical_price(self, asset_name):
        we = webcrawler.engine()
        data = we.get_data_from_table(settings.constants.all_currency[asset_name]['url'], settings.constants.all_currency[asset_name]['table_selector'])
        return data


