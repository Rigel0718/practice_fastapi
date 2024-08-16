from typing import Generator, Type, Optional
from sqlalchemy import create_engine, Column, Integer, Text, Enum, Boolean, ForeignKey, String
from database.db_config import DB_URL 
from sqlalchemy.orm import sessionmaker, relationship, Mapped, DeclarativeBase, Session
from sqlalchemy.future import select
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
    async def get_by_column(cls: Type["Base"], **kwargs) -> Optional["Base"]:
        async with get_db() as session:
            stmt = select(cls)
            for key, value in kwargs.items():
                column = getattr(cls, key)
                stmt = stmt.filter(column==value)
            result = await session.execute(stmt)
            return result.scalars().first()
    
    @classmethod
    async def build_and_add(cls: Type["Base"], **kwargs) -> "Base":
        async with get_db() as session:
            obj = cls()
            for column in obj.all_columns():
                column_name = column.name
                if column_name in kwargs:
                    setattr(obj, column_name, kwargs.get(column_name))
            session.add(obj)
            await session.flush() 
            return obj

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = Column(Integer, primary_key=True, index=True)
    name : Mapped[str] = Column(String(255), nullable=True)
    email : Mapped[str] = Column(String(255), nullable=True)
    pw : Mapped[str] = Column(String(1000), nullable=True)
    status : Mapped[str] = Column(Enum("active", "blocked", "deleted"), default="active")

if __name__  == "__main__":
    Base.metadata.create_all(bind = engine)
    with get_db() as session:
        user_instance = User()
        columns = user_instance.all_columns()
        for c in columns:
            print(c.name)
