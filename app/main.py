import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from routes import auth, user
from starlette.middleware.authentication import AuthenticationMiddleware
from middleware.auth_access import JWTAuthBackend
import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())

@app.get("/")
async def home():
    return {'message' : 'start'}


if __name__ == "__main__" :
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)