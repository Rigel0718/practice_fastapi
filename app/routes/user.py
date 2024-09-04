from fastapi import APIRouter, Depends, Request
from starlette.authentication import requires

router = APIRouter(prefix="/user", tags=['user'], responses={404: {"description": "Not found"}})


@router.post('/me', status_code=200)
@requires(['authenticated'])
async def user_detail(request: Request):
    return request.user