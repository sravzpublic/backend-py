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
    'sravz_upload_historical_vix_quotes',
    default_args=default_args,
    description='Upload historical vix quotes to mongodb',
    schedule='5 23 * * *',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'hetzner'],
) as dag:
    t1 = BashOperator(
        task_id='sravz_upload_historical_vix_quotes',
        bash_command='python /home/airflow/src/services/vix/historical_db_upload.py',
    )
