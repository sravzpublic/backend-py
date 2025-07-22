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
    'sravz_upload_current_weeks_earnings',
    default_args=default_args,
    description='Upload current week earnings to mongodb',
    schedule='*/60 10-16 * * 1-5', # Every hour weekday
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'contabo'],
) as dag:
    t1 = BashOperator(
        task_id='sravz_upload_current_weeks_earnings',
        bash_command='python -c "from src.services.earnings.db_upload import engine; engine().get_current_week_earnings_from_web(upload_to_db=True)"',
    )
