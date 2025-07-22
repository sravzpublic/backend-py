#!/usr/bin/env python
from src.services.iot_helpers import smarthings_reader

def update():
    sre = smarthings_reader.engine() 
    sre.get_smarthings_data_for_users()
    
if __name__ == '__main__':
    update()
