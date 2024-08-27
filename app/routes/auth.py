from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.orm_models import UserORM
from typing import Optional, Annotated
from database.schema import RegisterUserInform, User, Token
from operators.orm_operators import (
    get_by_email, 
    get_db, 
    is_email_exist_session, 
    commit_orm2db
)
from operators.auth_operators import (
    generated_hashed_pw,
    check_match_pw,
    orm2schema,
    schema2dict,
    build_ORM_by_schema,
    create_auth_token
)


router = APIRouter(prefix="/auth", tags=['auth'])


@router.post("/register", status_code=201, response_model=Token)
async def register(reg_user_info: RegisterUserInform, session: Annotated[Session, Depends(get_db)]):
    is_exist: bool = await is_email_exist_session(session, reg_user_info.email)
    if not reg_user_info.email or not reg_user_info.pw:
        raise HTTPException(status_code=400, detail="Email and pw NOT provided")
    if is_exist:
        raise HTTPException(status_code=400, detail="Email is already exist!!")
        
    reg_user_info.pw = generated_hashed_pw(reg_user_info.pw)
    new_user_orm = build_ORM_by_schema(UserORM, session, **schema2dict(reg_user_info))
    new_user = commit_orm2db(new_user_orm, session)
    usertoken_model : User = orm2schema(new_user)
    user_token_instance: str = create_auth_token(usertoken_model)
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token

@router.post("/login", status_code=200, response_model=Token)
async def login(user_info: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_db)]):
    entered_email = user_info.username
    entered_pw = user_info.password
    is_exist: bool = await is_email_exist_session(session, entered_email)
    if not entered_email or not entered_pw:
        raise HTTPException(status_code=400 , detail="Email and PW must be provied")
    if not is_exist:
        raise HTTPException(status_code=400, detail="No Match Users")
    user: Optional[UserORM] = get_by_email(UserORM, session=session, email=entered_email) 
    if not check_match_pw(hashed_pw=user.pw, plain_pw=entered_pw):
        raise HTTPException(status_code=401, detail="No Match Users")
    
    usertoken_model: User = orm2schema(user)
    user_token_instance: str = create_auth_token(usertoken_model)
    token = Token(Authorization_token=f'Bearer {user_token_instance}')
    return token