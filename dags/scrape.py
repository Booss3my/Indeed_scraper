from datetime import timedelta  
import os
import sys
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago 
from dotenv import load_dotenv

RPATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(RPATH)

from src.scraper import scrape
from src.loader import load_data
from src.staging_cleaner import clean 


load_dotenv(os.path.join(RPATH,".env"))

# initializing the default arguments that we'll pass to our DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(5)
}

ingestion_dag = DAG(
    'Indscraping_dag',
    default_args=default_args,
    description='Job offer records scraping',
    # schedule_interval=timedelta(minutes=1),
    catchup=False
)

task_1 = PythonOperator(
    task_id='ScrapeData_and_transform',
    python_callable=scrape,
    dag=ingestion_dag,
)

task_2 = PythonOperator(
    task_id='load_to_DB',
    python_callable=load_data,
    dag=ingestion_dag,
)

task_3 = PythonOperator(
    task_id='clean_staging_area',
    python_callable=clean,
    dag=ingestion_dag,
)


task_1 >> task_2 >> task_3