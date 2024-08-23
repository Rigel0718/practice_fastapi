from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request
import jwt
from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: int = None
    name: Optional[str] = None
    email: Optional[str] = None
    pw: Optional[str] = None
    status: str = None
    disabled: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

load_dotenv(verbose=True)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

class JWTACCESSMIDDLEware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization_token")
        if token.startswith("Bearer"):
            token = token.split(" ")[1]
            payload = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
            request.state.user = User(**payload)
        response = await call_next(request)
        return response

        