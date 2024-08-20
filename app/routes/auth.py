from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.orm_models import get_db, UserORM
from typing import Optional, Annotated
from pydantic import EmailStr, BaseModel, ConfigDict
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
import jwt

load_dotenv(verbose=True)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

router = APIRouter(prefix="/auth", tags=['auth'])

class RegisterUserInform(BaseModel):
    email: EmailStr = None
    pw : str = None

class User(BaseModel):
    id: int = None
    name: Optional[str] = None
    email: Optional[str] = None
    pw: Optional[str] = None
    status: str = None
    disabled: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    Authorization_token: str 
    token_type : str

async def is_email_exist_session(session: Session, email: str)-> bool:
    obtained_email: Optional[str] = UserORM.get_by_column(session=session, email=email)
    if obtained_email is None:
        return False
    return True

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

def generated_pw_hashed(plain_pw: str) -> str:
    return pwd_context.hash(plain_pw)

def check_match_pw(hashed_pw: str, plain_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)

def orm2schema(new_user: UserORM) -> User:
    return User.model_validate(new_user)

def create_auth_token(user_data: User) -> str:
    _user_data_dict = user_data.model_dump(exclude={'pw'})
    _encode = _user_data_dict.copy()
    jwt_encode = jwt.encode(_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jwt_encode

@router.post("/register", status_code=201, response_model=Token)
async def register(reg_user_info: RegisterUserInform, session: Annotated[Session, Depends(get_db)]):
    is_exist: bool = await is_email_exist_session(session, reg_user_info.email)
    if not reg_user_info.email or not reg_user_info.pw:
        HTTPException(status_code=400, detail="Email and pw NOT provided")
    if is_exist:
        HTTPException(status_code=400, detail="Email is already exist!!")
        
    hashed_pw = CryptContext(reg_user_info.pw)
    new_user : UserORM = UserORM.build_and_add(session=session,email=reg_user_info.email, pw=hashed_pw) #kwargs를 Enum으로 바꿔야할듯
    usertoken_model : User = orm2schema(new_user)
    session.commit()
    user_token_instance: str = create_auth_token(usertoken_model)
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token

@router.post("/login", status_code=200, response_model=Token)
async def login(user_info: RegisterUserInform, session: Annotated[Session, Depends(get_db)]):
    is_exist: bool = await is_email_exist_session(session, user_info.email)
    if not user_info.email or not user_info.pw:
        raise HTTPException(status_code=400 , detail="Email and PW must be provied")
    if not is_exist:
        raise HTTPException(status_code=400, detail="No Match Users")
    user: Optional[UserORM] = UserORM.get_by_email(session=session, email=user_info.email) 
    if not check_match_pw(hashed_pw=user.pw, pw=user_info.pw):
        raise HTTPException(status_code=401, detail="No Match Users")
    
    usertoken_model: User = orm2schema(user)
    user_token_instance: str = create_auth_token(usertoken_model)
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token