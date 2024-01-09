import psycopg2
import os

conn = psycopg2.connect(
    host="localhost",
    database="airflow",
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASS'])