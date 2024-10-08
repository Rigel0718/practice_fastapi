from fastapi.requests import HTTPConnection
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request
import jwt
from dotenv import load_dotenv
import os
from database.schema import User
from operators.auth_operators import get_current_user
from starlette.authentication import BaseUser, UnauthenticatedUser, SimpleUser, AuthenticationError, AuthCredentials, AuthenticationBackend

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
    

class JWTAuthBackend(AuthenticationBackend): 
    async def authenticate(self, conn): 
        print("HI_EEEEEEEEEEEEEEEE")
        guest = AuthCredentials(["unauthenticated"]), UnauthenticatedUser()

        if "Authorization" not in conn.headers:
            print(guest)
            return guest
        
        auth = conn.headers["Authorization"]
        try:
            scheme, token = auth.split(' ')
            if scheme != "Bearer":
                return guest
        except ValueError:
            AuthenticationError("Invalid bearer auth credentials")

        if not token :
            return guest
        
        user = get_current_user(token)

        if not user :
            return guest
        print("DDDDDDDDDDDDDDDDDDDDDDDFFFFFFF")
        print(AuthCredentials('authenticated'), user)
        print("DFFFFFFFFFGFRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        return AuthCredentials('authenticated'), user
        