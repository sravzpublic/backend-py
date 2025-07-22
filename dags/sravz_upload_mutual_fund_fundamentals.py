from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.decorators import task_group, task
from datetime import datetime, timedelta
from airflow import DAG
import sys
from src.util import helper
sys.path.append('/home/airflow/')


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['contactus@sravz.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    'sravz_upload_mutual_funds_fundamentals',
    default_args=default_args,
    description='Uploads Sravz Mutual Funds fundamentals to S3',
    schedule='0 0 * * *',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'hetzner'],
) as dag:

    @task
    def get_mutual_fund_fundamentals(tickers: list):
        from src.services.mutual_funds import fundamentals
        fundamental_engine = fundamentals.engine()
        # Fundamentals are saved with name: {ticker}_fundamental
        return fundamental_engine.get_fundamentals(tickers=tickers)

    @task_group
    def get_mutual_fund_fundamentals_group(tickers: list):
        return get_mutual_fund_fundamentals(tickers=tickers)
        
    from src.services.etfs import mutual_funds_historical_quotes
    from src.util import settings
    engine = mutual_funds_historical_quotes.engine()
    ticker_list =  engine.get_all_mf_tickers([], cache=True)
    ticker_list = sorted(ticker_list, key=lambda x: x['SravzId'])
    ticker_list = helper.get_list_part_based_on_day(ticker_list)

    n = int(len(ticker_list)/settings.constants.AIRFLOW_MAX_TASKS_IN_TASK_MAPPING)
    tickers = [ticker_list[i:i + n] for i in range(0, len(ticker_list), n)]
    _ = get_mutual_fund_fundamentals_group.expand(tickers=tickers)
