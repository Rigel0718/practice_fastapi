from typing import Generator
from sqlalchemy import create_engine, Column, Integer, Text, Enum, Boolean, ForeignKey, String
from db_config import DB_URL 
from sqlalchemy.orm import sessionmaker, relationship, Mapped, DeclarativeBase, Session
from contextlib import contextmanager

engine = create_engine(DB_URL, echo=True, pool_recycle=900)
Session_local = sessionmaker(autoflush=True, bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:

    try:
        local_session = Session_local()
        yield local_session
    finally:
        local_session.close()

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = Column(Integer, primary_key=True, index=True)
    name : Mapped[str] = Column(String(255), nullable=True)
    email : Mapped[str] = Column(String(255), nullable=True)
    pw : Mapped[str] = Column(String(1000), nullable=True)
    status : Mapped[str] = Column(Enum("active", "blocked", "deleted"), default="active")

if __name__  == "__main__":
    Base.metadata.create_all(bind = engine)
