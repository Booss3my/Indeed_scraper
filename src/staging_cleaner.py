import shutil 
import os
RPATH = os.path.dirname(os.path.dirname(__file__))

def clean():
    staging_path = os.path.join(RPATH,"staging")
    shutil.rmtree(staging_path)