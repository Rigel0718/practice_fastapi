from passlib.context import CryptContext
from database.orm_models import UserORM
from database.schema import RegisterUserInform, User, Token
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
import jwt
from jose import JWTError

load_dotenv(verbose=True)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

pw_context = CryptContext(schemes=["bcrypt"])
oauth2scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


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

def create_auth_token(user_data: User, expiered_delta: timedelta=timedelta(minutes=15)) -> str:
    payload = schema2dict(user_data, exclude={'pw'})
    expire_time = datetime.now(timezone.utc) + expiered_delta
    payload.update({"exp" : expire_time})
    _encode = payload.copy()
    jwt_encode = jwt.encode(_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jwt_encode

def get_token_payload(token: str) -> dict:
    try:
        payload: dict = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
    except JWTError:
        return None
    return payload


def get_current_user(token: Annotated[str, Depends(oauth2scheme)], session: Session) -> Optional[UserORM]:
    payload: Optional[dict] = get_token_payload(token)
    if (not payload) or (type(payload) is not dict) :
        return None
    
    user_email: Optional[str] = payload.get('email', None)
    if not user_email:
        return None
    
    stmt = select(UserORM).filter(UserORM.email==user_email)
    user: UserORM = session.execute(stmt).scalars().first()
    return user

