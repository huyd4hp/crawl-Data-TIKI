from threading import Thread
from sqlalchemy_utils import database_exists,create_database
from . import settings
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.base import Engine


class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
 
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
             
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    
def initDATABASE():
    '''
    DATABASE NAME - CONFIG in settings file
    '''
    ecommerce_engine = settings.ecommerce_engine
    #---------------
    if database_exists(ecommerce_engine.url) == False:
        create_database(ecommerce_engine.url)
        print(f"CREATE DATABASE {settings.ECOMMERCE_DB_DEFAULT} SUCCESSFULLY")
        settings.Metadata.create_all(ecommerce_engine)
    else:
        print("Database have already exist!")
    

def statusDATABASE():
    engine = settings.engine
    try:
        engine.connect()
        print("DATABASE READY")
        return True
    except SQLAlchemyError as error:
        print(error)
        return False

def ingestDATA(data:pd.DataFrame, engine:Engine):
    try:
        data.to_sql(name='product',con=engine,if_exists='append',index=False)
        print(f"Ingest {len(data)} rows into Database")
    except:
        print("Sorry, some error has occurred!")
    finally:
        engine.dispose()
    




