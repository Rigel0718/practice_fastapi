from typing import Generator, Type, Optional
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
    def __init__(self):
        pass

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]


    @classmethod
    def get(cls: Type["Base"], session: Optional[Session], **kwargs):
        if session is None:
            with get_db() as sess:
                return cls._get_from_session(sess,**kwargs)
        return cls._get_from_session(session,**kwargs)
    
    @classmethod
    def _get_from_session(cls: Type["Base"], session: Optional[Session], **kwargs):
        query = session.query(cls)
        for key, value in kwargs.items():
            column = getattr(cls, key)
            query = query.filter(column==value)

        result = query.one_or_none
        
        return result

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = Column(Integer, primary_key=True, index=True)
    name : Mapped[str] = Column(String(255), nullable=True)
    email : Mapped[str] = Column(String(255), nullable=True)
    pw : Mapped[str] = Column(String(1000), nullable=True)
    status : Mapped[str] = Column(Enum("active", "blocked", "deleted"), default="active")

if __name__  == "__main__":
    Base.metadata.create_all(bind = engine)
