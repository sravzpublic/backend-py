from __future__ import annotations
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
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
    'sravz_quotes_summary_stats',
    default_args=default_args,
    description='Calculate quotes summary stats and upload to S3',
    schedule='0 1 * * *',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'hetzner'],
) as dag:
            
    @task
    def get_single_ticker_stat(tickers: list):
        from src.services.stock import summary_stats
        summary_engine = summary_stats.engine()
        return summary_engine.get_summary_stats(tickers=tickers)
        
    @task
    def upload_ticker_stats(status):
        from src.services.stock import summary_stats
        summary_engine = summary_stats.engine()
        summary_engine.upload_final_stats_df()

    from src.services.stock import summary_stats
    from src.util import settings
    summary_engine = summary_stats.engine()
    ticker_list = summary_engine.get_all_tickers()
    n = int(len(ticker_list)/settings.constants.AIRFLOW_MAX_TASKS_IN_TASK_MAPPING)
    tickers = [ticker_list[i:i + n] for i in range(0, len(ticker_list), n)]
    status = get_single_ticker_stat.expand(tickers=tickers)
    upload_ticker_stats(status)
