#!/usr/bin/env python
from unittest.mock import Mock
import pytest

@pytest.fixture
def mock_mdbe(mocker):
    mock = Mock()
    mocker.patch('src.services.mdb.engine', return_value=mock)

    return mock

@pytest.fixture
def eodhistoricaldata(mocker):
    mock = Mock()
    mocker.patch('src.services.quotes_providers.eodhistoricaldata.engine', return_value=mock)    
    return mock


def test_upload_etfs_list(mock_mdbe, eodhistoricaldata):
    collection_mock = Mock()
    collection_mock.update_one = Mock()
    def side_effect_get_collection(*args, **kwargs):
        return collection_mock
    mock_mdbe.get_collection.side_effect = side_effect_get_collection
    mock_mdbe.get_collection_items.return_value = [{'Exchange Code': 'Fake'}]

    def side_effect_get_exchange_symbols(*args, **kwargs):
        return [{
        "SravzId" : "etf_us_fuinf",
        "APICode" : "FUINF.US",
        "Code" : "FUINF",
        "Country" : "USA",
        "Currency" : "USD",
        "Exchange" : "Fake",
        "Name" : "FUINF",
        "Type" : "ETF"
        }]   
    eodhistoricaldata.get_exchange_symbols.side_effect = side_effect_get_exchange_symbols       

    from src.services.assets import exchanges
    exchanges.upload_etfs_list()
    assert all([mock_call[1][1]['$set']['Country'] == "USA" for mock_call in collection_mock.update_one.mock_calls])

def test_upload_exchange_symbol_list(mock_mdbe, eodhistoricaldata):
    collection_mock = Mock()
    collection_mock.update_one = Mock()
    def side_effect_get_collection(*args, **kwargs):
        return collection_mock
    mock_mdbe.get_collection.side_effect = side_effect_get_collection
    mock_mdbe.get_collection_items.return_value = [{'Exchange Code': 'Fake'}]

    def side_effect_get_exchange_symbols(*args, **kwargs):
        return [{
        "SravzId" : "etf_us_fuinf",
        "APICode" : "FUINF.US",
        "Code" : "FUINF",
        "Country" : "USA",
        "Currency" : "USD",
        "Exchange" : "Fake",
        "Name" : "FUINF",
        "Type" : "ETF"
        }]   
    eodhistoricaldata.get_exchange_symbols.side_effect = side_effect_get_exchange_symbols    

    from src.services.assets import exchanges
    exchanges.upload_exchange_symbol_list()
    assert all([mock_call[1][1]['$set']['Country'] == "USA" for mock_call in collection_mock.update_one.mock_calls])    
