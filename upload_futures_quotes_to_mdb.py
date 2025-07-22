#!/usr/bin/env python
from src.services import price

def upload():
    price_engine = price.engine()
    price_engine.get_eodhistoricaldata_live_future_quotes()

if __name__ == '__main__':
    upload()

