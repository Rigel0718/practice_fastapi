from typing import Optional, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.orm_models import Base

T = TypeVar("T", bound="Base")

def get_by_column(cls: Type[T], session: Session,**kwargs) -> Optional[T]:
        stmt = select(cls)
        for key, value in kwargs.items():
            column = getattr(cls, key)
            stmt = stmt.filter(column==value)
        result = session.execute(stmt)
        return result.scalars().first()