from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.orm_models import get_db, User
from typing import Optional
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

async def is_email_exist_session(email: str)-> bool:
    obtained_email: Optional[str] = User.get_by_column(email=email)

    if obtained_email is None:
        return False
    return True

async def generated_pw_hashed(pw: str):
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())

def check_match_pw(hashed_pw, pw: str) -> bool:
    return bcrypt.checkpw(pw.encode("utf-8"), hashed_pw)

def create_auth_token(user_data: dict) -> str:
    _encode = user_data.copy()
    jwt_encode = jwt.encode(_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jwt_encode

@router.post("/register", status_code=201, response_model=Token)
async def register(reg_user_info: RegisterUserInform, session: Session = Depends(get_db)):
    is_exist: bool = await is_email_exist_session(reg_user_info.email)
    if not reg_user_info.email or not reg_user_info.pw:
        JSONResponse(status_code=400, content=dict(msg="Email and pw NOT provided"))
    if is_exist:
        JSONResponse(status_code=400, content=dict(msg="Email is already exist!!"))
        
    hashed_pw = await generated_pw_hashed(reg_user_info.pw)
    if not check_match_pw(hashed_pw, reg_user_info.pw):
        raise Exception("DO NOT Match encryped pw and normal pw")
    new_added_user : User = User.build_and_add(email=reg_user_info.email, pw=hashed_pw) #kwargs를 Enum으로 바꿔야할듯
    usertoken_model = UserToken.model_validate(new_added_user)
    user_token_instance: str = create_auth_token(usertoken_model.model_dump(exclude={'pw'}))
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token