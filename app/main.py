import uvicorn
from fastapi import FastAPI
from routes import auth

app = FastAPI()
app.include_router(auth.router)
@app.get("/")
async def home():
    return {'message' : 'start'}


if __name__ == "__main__" :
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)