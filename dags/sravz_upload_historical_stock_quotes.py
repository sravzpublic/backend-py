from __future__ import annotations
from datetime import datetime, timedelta
from airflow import DAG
from datetime import datetime, timedelta
from airflow import DAG
from datetime import datetime
from airflow import DAG
from airflow.decorators import task, task_group
from datetime import datetime, timedelta
from airflow import DAG
import sys
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

@task
def get_tickers():
    from src.services.stock.historical_quotes import engine
    from src.util import settings
    historical_quotes_engine = engine()
    ticker_list = historical_quotes_engine.get_tickers()
    n = int(len(ticker_list)/settings.constants.AIRFLOW_MAX_TASKS_IN_TASK_MAPPING)
    return [ticker_list[i:i + n] for i in range(0, len(ticker_list), n)]
        
@task
def upload_ticker(tickers: list):
    from src.services.stock import historical_quotes
    for ticker in tickers:
        historical_quotes.upload_ticker(ticker=ticker)

with DAG(
    'sravz_upload_historical_stock_quotes',
    default_args=default_args,
    description='Upload historical futures quotes to mongodb',
    schedule='0 21 * * *',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'hetzner'],
) as dag:
        
    @task_group
    def upload_ticker_task_group(tickers):
        upload_ticker(tickers)

    upload_ticker_task_group.expand(tickers=get_tickers())