from datetime import datetime, timedelta
from textwrap import dedent
from airflow import DAG
from airflow.operators.bash import BashOperator

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
    'sravz_calculate_portfolio_pnl',
    default_args=default_args,
    description='Calculates Portfolios PNL',
    schedule='0 0 * * 2-6',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'contabo'],
) as dag:
    t1 = BashOperator(
        task_id='sravz_calculate_portfolio_pnl',
        bash_command='python -c "from src.analytics.pnl import engine;engine().update()"',
    )
