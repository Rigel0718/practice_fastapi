from sqlalchemy import create_engine, Column, Integer, Text
from db_config import DB_URL 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine(DB_URL, echo=True, pool_recycle=900)
Session_local = sessionmaker(autoflush=True, bind=engine)

Base = declarative_base()