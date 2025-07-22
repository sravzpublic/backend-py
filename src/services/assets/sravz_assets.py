#!/usr/bin/env python
import json, datetime
from src.services import mdb
from src. util import settings
from src.util import settings, logger

_logger = logger.RotatingLogger(__name__).getLogger()

def upload_assets(source = 'quotes_collection'):
    mdbe = mdb.engine()
    if source == 'file':
        quotes_data = None
        with open('data\quotes.json') as data_file:
            quotes_data = json.load(data_file)
        if quotes_data:
            for element in quotes_data:
                for key in list(set(element.keys()) - set(["SravzId", "Commodity", "Country", "Month"])):
                    del element[key]
                element['Name'] = element.pop('Commodity')
                element['Type'] = 'Future'
            mdbe.upsert_to_collection("assets", quotes_data)
            mdbe.create_index_collection("assets", "SravzId")
        else:
            print("Quotes data not found")
    elif source == 'quotes_collection':
            data = []
            for element in mdbe.get_collection_items("quotes_stocks"):
                for key in list(set(element.keys()) - set(["SravzId", "Name", "Country", "Ticker", "Exchange"])):
                    del element[key]
                element['Type'] = 'Stock'
                element['Created'] = datetime.datetime.now(datetime.UTC)
                data.append(element)
            _logger.info('Obtained stock assets')

            for element in mdbe.get_collection_items("quotes_rates"):
                for key in list(set(element.keys()) - set(["SravzId", "Name", "Ticker", "Country", "Exchange"])):
                    del element[key]
                element['Type'] = 'Rate'
                element['Created'] = datetime.datetime.now(datetime.UTC)
                data.append(element)
            _logger.info('Obtained rates assets')

            for element in mdbe.get_collection_items("quotes_vix"):
                for key in list(set(element.keys()) - set(["SravzId", "Name", "Ticker", "Country", "Exchange"])):
                    del element[key]
                    element['Type'] = 'Vix'
                    element['Exchange'] = 'CBOE'
                    element['Country'] = 'US'
                    element['Created'] = datetime.datetime.now(datetime.UTC)
                    data.append(element)
                _logger.info('Obtained vix assets')

            # EOD assets
            for collection in settings.constants.ASSET_COLLECTION_LIST:
                if collection == settings.constants.EXCHANGE_SYMBOLS_COLLECTION:
                    # Upload US Mutual Funds only
                    for element in mdbe.get_collection_items(collection):
                        if element.get('Country') == "USA" and element.get('Exchange') == "NMFQS":
                            element.pop('_id')
                            element['Created'] = datetime.datetime.now(datetime.UTC)
                            data.append(element)
                    _logger.info(f'Obtained {collection} assets')
                elif collection == settings.constants.ETF_ASSETS_COLLECTION:
                    # Upload US ETFs only
                    for element in mdbe.get_collection_items(collection):
                        if element.get('Country') == "USA":
                            element.pop('_id')
                            element['Created'] = datetime.datetime.now(datetime.UTC)
                            data.append(element)
                    _logger.info(f'Obtained {collection} assets')
                else:
                    for element in mdbe.get_collection_items(collection):
                        element.pop('_id')
                        element['Created'] = datetime.datetime.now(datetime.UTC)
                        data.append(element)
                    _logger.info(f'Obtained {collection} assets')

            mdbe.upsert_to_collection("assets", data)
            mdbe.create_index_collection("assets", "SravzId")
            _logger.info('Uploaded assets')