#!/usr/bin/env python
from src.services import ecocal

def upload():
    ecocal_engine = ecocal.engine()
    ecocal_engine.get_current_week_eco_cal_from_web(upload_to_db = True) 

if __name__ == '__main__':
    upload()
    
