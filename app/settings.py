from sqlalchemy import Column,BIGINT,String,Float
from sqlalchemy import MetaData,Table
from sqlalchemy import create_engine
import os

# DATABASE INFORMATION
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = '131073'
HOST = '127.0.0.1'
PORT = '5432'

ECOMMERCE_DB_DEFAULT = 'Ecommerce' 
# Engine
ecommerce_engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{ECOMMERCE_DB_DEFAULT}", 
)
engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}", 
)
# PARAMETER FOR REQUEST 
proxies = { 
    "http"  : "http://192.168.43.1:10809",
    "https" : "https://192.168.43.1:10809"
}
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47'
}   
# TABLE OF ECOMMERCE_DB
Metadata = MetaData()
Product = Table(
    'product',
    Metadata,
    Column("id", BIGINT, primary_key=True),
    Column("source", String, primary_key=True),
    Column("name", String),
    Column("description", String),
    Column('price', Float),
    Column('url', String),
    Column('rate', Float),
    Column('category', String)
)
# DIRECTORY
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

