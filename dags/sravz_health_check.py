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
    'sravz_health_check',
    default_args=default_args,
    description='Performs sravz infrastructure health check',
    schedule='*/15 * * * *',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz'],
) as dag:
    t1 = BashOperator(
        task_id='sravz_health_check',
        bash_command='python /home/airflow/src/util/health_check.py',
    )
