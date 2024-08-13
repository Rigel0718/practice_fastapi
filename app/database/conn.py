from sqlalchemy import create_engine
from db_config import DB_URL 
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

engine = create_engine(DB_URL, echo=True, pool_recycle=900)