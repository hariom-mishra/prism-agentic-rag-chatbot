from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schema.user import UserSignUp, UserLogin, UserResponse
from services.users_services import UserService
from core.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    res = await service.login_user(credentials.email, credentials.password)
    
    # Generate auth token and refresh token
    access_token = create_access_token(res)
    refresh_token = create_refresh_token(res)

    return JSONResponse(status_code=200, content={
        "message": "User logged in successfully", 
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "user": UserResponse.model_validate(res).model_dump()
    })

@router.post("/signup")
async def signup(user: UserSignUp, db: AsyncSession = Depends(get_db)):
    # Since Pydantic performs validation, manual checks for existence of fields are redundant.
    # We can explicitly set the role to 'user' in case it was modified.
    user.role = "user"
    
    service = UserService(db)
    result = await service.create_user(user)
    
    return JSONResponse(status_code=200, content={
        "message": "User created successfully",
        "user": UserResponse.model_validate(result).model_dump()
    })