from src.util import settings, logger, helper
from src.services import webcrawler


class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.we = webcrawler.engine()
        self.INDEX_COUNTRY = {
            'FTSE': 'UK',
            'CAC': 'FR',
            'DAX': 'DE',
            'SGX': 'SG',
            'NIKKEI': 'JP',
            'STRAITS': 'SG',
            'HANG': 'HK',
            'TAIWAN': 'TW',
            'KOSPI': 'KR',
            'SET': 'TH',
            'JAKARTA': 'ID',
            'SHANGHAI': 'CN'
        }

    """description of class"""
    def get_world_index_quotes(self):
        url = 'https://www.moneycontrol.com/markets/global-indices/'
        data = self.we.get_data_from_html_table(None, 'mctable1 n18_res_table responsive tbl_scroll_resp', url=url)
        quotes = []
        for item in data:
            quote = {}
            if 'MARKETS' in item['Name']:
                continue
            quote['Name'] = ('_').join(item['Name'].split(' (')[:-1])
            quote['Ticker'] = quote['Name'].replace(' ', '_').lower()
            try:
                quote['Country'] = [self.INDEX_COUNTRY[key] for key in self.INDEX_COUNTRY if key.lower() in  item['Name'].lower()].pop()
            except:
                continue
            quote['SravzId'] = "idx_%s_%s"%(quote['Country'].lower() , quote['Ticker'].lower())
            quote['Change'] = helper.util.getfloat(item.pop('Change\n%Change').split('\n\n')[0])
            quote['PercentChange'] = item.pop('%Change')
            quote['Last'] = helper.util.getfloat(item.pop('CurrentValue'))
            quote['DayOpen'] = helper.util.getfloat(item.pop('Open\nPrev.Close').split('\n')[0])
            quote['PreviousClose'] = helper.util.getfloat(item.pop('Prev.Close'))
            quote['DayHigh'] = helper.util.getfloat(item.pop('High\nLow').split('\n')[0])
            quote['DayLow'] = helper.util.getfloat(item.pop('Low'))
            quotes.append(quote)
        return quotes

