from passlib.context import CryptContext
from database.orm_models import UserORM
from database.schema import RegisterUserInform, User, Token
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import jwt

load_dotenv(verbose=True)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


pw_context = CryptContext(schemes=["bcrypt"])

def generated_hashed_pw(plain_pw: str) -> str:
    return pw_context.hash(plain_pw)

def check_match_pw(hashed_pw: str, plain_pw: str) -> bool:
    return pw_context.verify(plain_pw, hashed_pw)

def orm2schema(new_user: UserORM) -> User:
    return User.model_validate(new_user)

def schema2dict(schema: User, exclude=None):
    return schema.model_dump(exclude=exclude)

def build_ORM_by_schema(orm_model: UserORM, **kwargs):
    orm_model_instance = orm_model()
    for column in orm_model_instance.all_columns():
        column_name = column.name
        if column_name in kwargs:
            setattr(orm_model_instance, column_name, kwargs.get(column_name))
    return orm_model_instance

def commit_orm2db(orm_model: UserORM, session: Session):
    session.add(orm_model)
    session.commit()
    session.refresh(orm_model)
    return orm_model

def create_auth_token(user_data: User, expiered_delta: timedelta=timedelta(minutes=15)) -> str:
    _user_data_dict = schema2dict(user_data, exclude={'pw'})
    expire_time = datetime.now(timezone.utc) + expiered_delta
    _user_data_dict.update({"exp" : expire_time})
    _encode = _user_data_dict.copy()
    jwt_encode = jwt.encode(_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jwt_encode
