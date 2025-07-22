#!/usr/bin/env bash
set -x
#Uploads currenet future prices from CNBC
/home/ubuntu/.virtualenvs/python3.6/bin/python upload_quotes_to_mdb.py
#Uploads ecocal
/home/ubuntu/.virtualenvs/python3.6/bin/python upload_ecocal_to_mdb.py
#Uploads all prices from Quandl. Run this rarely
#/home/ubuntu/.virtualenvs/python3.6/bin/python upload_futures_price_to_mdb.py
#/home/ubuntu/.virtualenvs/python3.6/bin/python upload_stats.py
/home/ubuntu/.virtualenvs/python3.6/bin/python upload_sravz_assets.py
/home/ubuntu/.virtualenvs/python3.6/bin/python update_portfolio_pnl.py
/home/ubuntu/.virtualenvs/python3.6/bin/python upload_snp_components.py 
#Uses various sites to upload current quote
/home/ubuntu/.virtualenvs/python3.6/bin/python upload_snp_quotes_to_mdb.py
#Uploads historical quotes from Google
/home/ubuntu/.virtualenvs/python3.6/bin/python upload_snp_quotes_to_historical_mdb.py
echo "All jobs complete"