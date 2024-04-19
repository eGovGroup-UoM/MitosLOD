from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

from asyncMain import main_async
from TTLGeneralOutput import main_transform
from upload import upload_ttl_to_virtuoso
import asyncio

def fetch_mitos_data():
    asyncio.run(main_async())

def generate_ttl():
    main_transform()

def upload_ttl():
    ttl_file = "dags/data/generated_data.ttl"
    virtuoso_url = "https://virtuoso-1706142355.p1.bdti.dataplatform.tech.ec.europa.eu"
    graph_uri = "https://mitos.gov.gr:8890/"
    username = "dba"
    password = "o8e4CQv5olQf87sT"
    upload_ttl_to_virtuoso(ttl_file, virtuoso_url, graph_uri, username, password)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 19)
}

# Define the DAG
with DAG('mitos_transformation', default_args=default_args, schedule_interval='0 8 * * 7') as dag:

    fetch_task = PythonOperator(
        task_id='Fetch_Mitos_Data',
        python_callable=fetch_mitos_data,
    )

    generate_task = PythonOperator(
        task_id='Generate_TTL',
        python_callable=generate_ttl,
    )

    upload_task = PythonOperator(
        task_id='Upload_TTL',
        python_callable=upload_ttl,
    )

    # Set task dependencies (task_1 -> task_2)
    fetch_task >> generate_task >> upload_task
