#!/usr/bin/env python
import json
from src.services import mdb

def upload_fake_user():
    mdbe = mdb.engine()
    fake_user_data = None
    with open('./data/fake_user.json') as data_file:
        fake_user_data = json.load(data_file)
    if fake_user_data:
        print(fake_user_data)
        mdbe.upsert_to_collection("users", fake_user_data, upsert_clause_field = '_id')
    else:
        pass
            
if __name__ == '__main__':
    upload_fake_user()