from src.util import settings, logger
from src.services import webcrawler

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()

    def get_list_of_indexes(self):
        url = "https://eodhistoricaldata.com/api/exchanges/INDX?api_token={0}&fmt=json".format(settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_list_of_govt_bonds(self):
        url = "https://eodhistoricaldata.com/api/exchanges/GBOND?api_token={0}&fmt=json".format(settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_list_of_crypto(self):
        url = "https://eodhistoricaldata.com/api/exchanges/cc?api_token={0}&fmt=json".format(settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_list_of_currencies(self):
        url = "https://eodhistoricaldata.com/api/exchanges/forex?api_token={0}&fmt=json".format(settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_index_components(self, index_code, index_exchange):
        # https://eodhistoricaldata.com/api/fundamentals/GSPC.INDX?api_token=
        url = "https://eodhistoricaldata.com/api/fundamentals/{0}.{1}?api_token={2}&fmt=json".format(index_code, index_exchange, settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_exchange_components(self, exchange_code):
        # https://eodhistoricaldata.com/api/exchanges/nse?api_token=
        url = "https://eodhistoricaldata.com/api/exchanges/{0}?api_token={1}&fmt=json".format(exchange_code, settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_exchange_symbols(self, exchange_code):
        url = "https://eodhistoricaldata.com/api/exchange-symbol-list/{0}?api_token={1}&fmt=json".format(exchange_code, settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_futures_symbols(self):
        url = "https://eodhistoricaldata.com/api/exchange-symbol-list/COMM?api_token={0}&fmt=json".format(settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')

    def get_bond_symbols(self):
        url = "https://eodhistoricaldata.com/api/exchange-symbol-list/BOND?api_token={0}&fmt=json".format(settings.constants.EODHISTORICALDATA_API_KEY)
        self.logger.info("processing %s"%(url))
        return self.we.get_data_from_url(url, return_type = 'json')
