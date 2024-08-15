from sqlalchemy import create_engine, Column, Integer, Text, Enum, Boolean, ForeignKey, String
from db_config import DB_URL 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Mapped

engine = create_engine(DB_URL, echo=True, pool_recycle=900)
Session_local = sessionmaker(autoflush=True, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = Column(Integer, primary_key=True, index=True)
    name : Mapped[str] = Column(String, nullable=True)
    email : Mapped[str] = Column(String, nullable=True)
    status : Mapped[str] = Column(Enum("active", "blocked", "deleted"))
