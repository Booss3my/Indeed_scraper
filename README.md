# Indeed web scraper



![scraper](https://user-images.githubusercontent.com/56868809/157312375-1e0890cd-2ceb-467d-b1ec-3368f35f9073.png)





# Troubleshoosting

If airflow-init breaks due to no database "airflow" in the postgres container, you can go in the postgres container and create the database then rerun the build file:

exec -it docker_postgres_1 
createdb -h localhost -U airflow airflow

// exit the container (Ctrl+D)
// Make sure you're in the root folder

sh build.sh