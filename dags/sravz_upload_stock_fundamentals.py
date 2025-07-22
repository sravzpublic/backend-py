from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.decorators import task_group, task
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

with DAG(
    'sravz_upload_stock_fundamentals',
    default_args=default_args,
    description='Uploads Sravz Stock fundamentals to S3',
    schedule='0 0 * * SAT',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'hetzner'],
) as dag:

    @task
    def get_stock_fundamentals(tickers: list):
        from src.services.stock import summary_stats
        summary_engine = summary_stats.engine()
        return summary_engine.get_fundamentals(tickers=tickers)

    @task_group
    def get_stock_fundamentals_group(tickers: list):
        return get_stock_fundamentals(tickers=tickers)
        
    from src.services.stock import summary_stats
    from src.util import settings    
    summary_engine = summary_stats.engine()
    ticker_list = summary_engine.get_all_fundamental_tickers()
    n = int(len(ticker_list)/settings.constants.AIRFLOW_MAX_TASKS_IN_TASK_MAPPING)
    tickers = [ticker_list[i:i + n] for i in range(0, len(ticker_list), n)]
    _ = get_stock_fundamentals_group.expand(tickers=tickers)
