FROM apache/airflow:2.8.0
ADD requirements.txt .
RUN pip install apache-airflow==2.8.0 -r requirements.txt