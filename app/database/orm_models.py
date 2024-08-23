from typing import Generator, Type, Optional, TypeVar
from sqlalchemy import create_engine, Integer, Enum, Boolean, ForeignKey, String, select
from database.db_config import DB_URL 
from sqlalchemy.orm import sessionmaker, relationship, Mapped, DeclarativeBase, Session, mapped_column
from sqlalchemy.future import select
import sys
from os import path

engine = create_engine(DB_URL, echo=True, pool_recycle=900)
Session_local = sessionmaker(autoflush=True, bind=engine)


def get_db() -> Generator[Session, None, None]:
    local_session = Session_local()
    try:
        yield local_session
    finally:
        local_session.close()

T = TypeVar("T", bound="Base")

class Base(DeclarativeBase):
    def __init__(self):
        pass

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]
    
    @classmethod
    def all_columns_cls(cls):
        return [c for c in cls.__table__.columns if c.primary_key is False and c.name != "created_at"]    
    


class UserORM(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String(255), nullable=True)
    email : Mapped[str] = mapped_column(String(255), nullable=True)
    pw : Mapped[str] = mapped_column(String(1000), nullable=True)
    status : Mapped[str] = mapped_column(Enum("active", "blocked", "deleted"), default="active")

if __name__  == "__main__":
    app_dir_path = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(app_dir_path)
    # Base.metadata.drop_all(bind=engine, tables=[User.__table__])
    with engine.begin() as conn:
        Base.metadata.create_all(bind = engine)
    example_users = [
        {"name": "SSS", "email": "alice@example.com", "pw": "hashed_password_1"},
        {"name": "KKK", "email": "bob@example.com", "pw": "hashed_password_2"},
        {"name": "UUUU", "email": "charlie@example.com", "pw": "hashed_password_3"}
    ]
    with get_db() as session:
        for user_info in example_users:
            UserORM.build_and_add(**user_info)
        