from fastapi import APIRouter, Depends
from pydantic import EmailStr
import bcrypt
import jwt


router = APIRouter(prefix="/auth")

@router.post("/register", status_code=201)
async def register(reg_user_info):
    # 등록을 원하는 사용자의 정보에 중복이 있는지?
    # pw 해싱