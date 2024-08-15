from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.orm_models import get_db
from typing import bool
from pydantic import EmailStr, BaseModel
import bcrypt
import jwt


router = APIRouter(prefix="/auth")

class RegisterUserInform(BaseModel):
    email: EmailStr = None
    pw : str = None

@router.post("/register", status_code=201)
async def register(reg_user_info: RegisterUserInform, session: Session = Depends(get_db)):
    is_exist: bool 
    