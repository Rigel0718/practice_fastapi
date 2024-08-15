from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.orm_models import get_db, User
from typing import bool, Optional
from pydantic import EmailStr, BaseModel
from starlette.responses import JSONResponse
import bcrypt
import jwt


router = APIRouter(prefix="/auth")

class RegisterUserInform(BaseModel):
    email: EmailStr = None
    pw : str = None

async def is_email_exist_session(email: str)-> bool:
    obtained_email: Optional[str] = User.get(email=email)

    if obtained_email is None:
        return False
    return True

async def generated_pw_hashed(pw: str):
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())

@router.post("/register", status_code=201)
async def register(reg_user_info: RegisterUserInform, session: Session = Depends(get_db)):
    is_exist: bool = await is_email_exist_session(reg_user_info.email)
    if not reg_user_info.email or not reg_user_info.pw:
        JSONResponse(status_code=400, content=dict(msg="Email and pw NOT provided"))
    if is_exist:
        JSONResponse(status_code=400, content=dict(msg="Email is already exist!!"))
        
    hashed_pw = await generated_pw_hashed(reg_user_info.pw)