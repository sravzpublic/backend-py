#!/usr/bin/env python
from src.services import price

def upload():
    '''
        Upload today's price only
    '''
    price_engine = price.engine()
    price_engine.get_eodhistoricaldata_historical_future_quotes()


if __name__ == '__main__':
    upload()

