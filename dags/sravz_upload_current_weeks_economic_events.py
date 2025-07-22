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
    'sravz_upload_current_weeks_economic_events',
    default_args=default_args,
    description='Upload current week economic events to mongodb',
    schedule='5 9-16 * * 1-5',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['sravz', 'contabo'],
) as dag:
    t1 = BashOperator(
        task_id='sravz_upload_current_weeks_economic_events',
        bash_command='python -c "from src.services.economic_events.db_upload import engine; engine().get_current_week_economic_events_from_web(upload_to_db=True)"',
    )
