from pydantic import EmailStr, BaseModel, ConfigDict
from typing import Optional

class RegisterUserInform(BaseModel):
    name : str
    email: EmailStr = None
    pw : str = None

    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    id: int = None
    name: Optional[str] = None
    email: Optional[str] = None
    pw: Optional[str] = None
    status: str = None
    disabled: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    Authorization_token: str 
    token_type : str = "Bearer"