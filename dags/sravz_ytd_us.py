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
    'sravz_ytd',
    default_args=default_args,
    description='Calculate YTD and upload to S3',
    schedule='0 1 * * *',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'hetzner'],
) as dag:
    t1 = BashOperator(
        task_id='sravz_ytd',
        bash_command='python /home/airflow/src/analytics/ytd.py',
    )
