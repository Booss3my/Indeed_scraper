import pandas as pd
import os
from sqlalchemy import create_engine

RPATH = os.path.dirname(os.path.dirname(__file__))
staging_path = os.path.join(RPATH,"staging")

def load_data():
    #Env vars
    _user = os.environ["DB_USER"]  
    _pass = os.environ["DB_PASS"]
    _host = os.environ["DB_HOST"]
    _name = os.environ["DB_NAME"]
    
    engine = create_engine(f'postgresql://{_user}:{_pass}@{_host}:5432/{_name}')

    
    df=pd.read_csv("staging/offers.csv") #read file from staging path
    df.to_sql('jobs', engine,if_exists='append') 
