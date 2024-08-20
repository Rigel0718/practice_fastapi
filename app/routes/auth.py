from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.orm_models import get_db
from database import orm_models
from typing import Optional, Annotated
from pydantic import EmailStr, BaseModel, ConfigDict
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import os
import bcrypt
import jwt

load_dotenv(verbose=True)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

router = APIRouter(prefix="/auth")

class RegisterUserInform(BaseModel):
    email: EmailStr = None
    pw : str = None

class UserToken(BaseModel):   # 이런 요소들을 Enum에서 한번에 관리해야겠다.. 중복했다가 실수할 확률 높음
    id: int = None
    name: Optional[str] = None
    email: Optional[str] = None
    pw: Optional[str] = None
    status: str = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    Authorization_token: str 

async def is_email_exist_session(session: Session, email: str)-> bool:
    obtained_email: Optional[str] = orm_models.User.get_by_column(session=session, email=email)

    if obtained_email is None:
        return False
    return True

def generated_pw_hashed(pw: str):
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())

def check_match_pw(hashed_pw: str, pw: str) -> bool:
    return bcrypt.checkpw(pw.encode("utf-8"), hashed_pw.encode("utf-8"))

def create_auth_token(user_data: dict) -> str:
    _encode = user_data.copy()
    jwt_encode = jwt.encode(_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jwt_encode

@router.post("/register", status_code=201, response_model=Token)
async def register(reg_user_info: RegisterUserInform, session: Annotated[Session, Depends(get_db)]):
    is_exist: bool = await is_email_exist_session(session, reg_user_info.email)
    if not reg_user_info.email or not reg_user_info.pw:
        HTTPException(status_code=400, detail="Email and pw NOT provided")
    if is_exist:
        HTTPException(status_code=400, detail="Email is already exist!!")
        
    hashed_pw = generated_pw_hashed(reg_user_info.pw)
    
    new_added_user : orm_models.User = orm_models.User.build_and_add(session=session,email=reg_user_info.email, pw=hashed_pw) #kwargs를 Enum으로 바꿔야할듯
    usertoken_model : UserToken = UserToken.model_validate(new_added_user)
    session.commit()
    user_token_instance: str = create_auth_token(usertoken_model.model_dump(exclude={'pw'}))
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token

@router.post("/login", status_code=200, response_model=Token)
async def login(user_info: RegisterUserInform, session: Annotated[Session, Depends(get_db)]):
    is_exist: bool = await is_email_exist_session(session, user_info.email)
    if not user_info.email or not user_info.pw:
        raise HTTPException(status_code=400 , detail="Email and PW must be provied")
    if not is_exist:
        raise HTTPException(status_code=400, detail="No Match Users")
    user: Optional[orm_models.User] = orm_models.User.get_by_email(session=session, email=user_info.email) 
    if not check_match_pw(hashed_pw=user.pw, pw=user_info.pw):
        raise HTTPException(status_code=401, detail="No Match Users")
    usertoken_model : UserToken = UserToken.model_validate(user)
    user_token_instance: str = create_auth_token(usertoken_model.model_dump(exclude={'pw'}))
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token