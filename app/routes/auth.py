from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.orm_models import UserORM
from typing import Optional, Annotated
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from database.schema import RegisterUserInform, User, Token
from operators.orm_operators import get_by_email, build_and_add, get_db

load_dotenv(verbose=True)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

router = APIRouter(prefix="/auth", tags=['auth'])
pw_context = CryptContext(schemes=["bcrypt"])

async def is_email_exist_session(session: Session, email: str)-> bool:
    obtained_email: Optional[str] = get_by_email(UserORM, session=session, email=email)
    if obtained_email is None:
        return False
    return True

def generated_hashed_pw(plain_pw: str) -> str:
    return pw_context.hash(plain_pw)

def check_match_pw(hashed_pw: str, plain_pw: str) -> bool:
    return pw_context.verify(plain_pw, hashed_pw)

def orm2schema(new_user: UserORM) -> User:
    return User.model_validate(new_user)

def schema2dict(schema: User, exclude=None):
    return schema.model_dump(exclude=exclude)

def build_ORM_by_schema(orm_model: UserORM, session: Session, **kwargs):
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
    # _user_data_dict = user_data.model_dump(exclude={'pw'})
    _user_data_dict = schema2dict(user_data, exclude={'pw'})
    expire_time = datetime.now(timezone.utc) + expiered_delta
    _user_data_dict.update({"exp" : expire_time})
    _encode = _user_data_dict.copy()
    jwt_encode = jwt.encode(_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jwt_encode

@router.post("/register", status_code=201, response_model=Token)
async def register(reg_user_info: RegisterUserInform, session: Annotated[Session, Depends(get_db)]):
    is_exist: bool = await is_email_exist_session(session, reg_user_info.email)
    if not reg_user_info.email or not reg_user_info.pw:
        raise HTTPException(status_code=400, detail="Email and pw NOT provided")
    if is_exist:
        raise HTTPException(status_code=400, detail="Email is already exist!!")
        
    reg_user_info.pw = generated_hashed_pw(reg_user_info.pw)
    new_user_orm = build_ORM_by_schema(UserORM, session, **schema2dict(reg_user_info))
    new_user = commit_orm2db(new_user_orm, session)
    usertoken_model : User = orm2schema(new_user)
    user_token_instance: str = create_auth_token(usertoken_model)
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token

@router.post("/login", status_code=200, response_model=Token)
async def login(user_info: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_db)]):
    entered_email = user_info.username
    entered_pw = user_info.password
    is_exist: bool = await is_email_exist_session(session, entered_email)
    if not entered_email or not entered_pw:
        raise HTTPException(status_code=400 , detail="Email and PW must be provied")
    if not is_exist:
        raise HTTPException(status_code=400, detail="No Match Users")
    user: Optional[UserORM] = get_by_email(UserORM, session=session, email=entered_email) 
    if not check_match_pw(hashed_pw=user.pw, plain_pw=entered_pw):
        raise HTTPException(status_code=401, detail="No Match Users")
    
    usertoken_model: User = orm2schema(user)
    user_token_instance: str = create_auth_token(usertoken_model)
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token