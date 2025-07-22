#!/usr/bin/env python
from src.services.nahb import engine
from src.util.settings import constants

def upload():
    nahb_engine = engine()
    nahb_engine.upload_quandl_to_s3(constants.quotes['int_nahb_forecast'], 'int_nahb_forecast')

if __name__ == '__main__':
    upload()

