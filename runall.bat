setlocal
cd /d %~dp0
python fetch_commodities_price.py
python upload_quotes_to_mdb.py
python upload_ecocal_to_mdb.py
python upload_futures_price_to_mdb.py
python upload_stats.py
python upload_sravz_assets.py
python update_portfolio_pnl.py
python upload_snp_components.py 
python upload_snp_quotes_to_mdb.py
python upload_snp_quotes_to_historical_mdb.py
echo "All jobs complete"

