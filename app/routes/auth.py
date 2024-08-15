from fastapi import APIRouter, Depends
from pydantic import EmailStr
import bcrypt
import jwt


router = APIRouter(prefix="/auth")