#!/usr/bin/env python
from src.services.treasury import engine
from src.util.settings import constants

def upload():
    treasury_engine = engine()
    treasury_engine.upload_quandl_to_s3(constants.quotes['treasury_real_longterm_rate'], 'treasury_real_longterm_rate')
    treasury_engine.upload_quandl_to_s3(constants.quotes['treasury_real_yieldcurve_rate'], 'treasury_real_yieldcurve_rate')
    treasury_engine.upload_quandl_to_s3(constants.quotes['treasury_bill_rate'], 'treasury_bill_rate')
    treasury_engine.upload_quandl_to_s3(constants.quotes['treasury_long_term_rate'], 'treasury_long_term_rate')

if __name__ == '__main__':
    upload()

