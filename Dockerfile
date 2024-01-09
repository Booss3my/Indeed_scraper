FROM apache/airflow:2.8.0
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt
