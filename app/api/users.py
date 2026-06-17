from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schema.user import UserResponse
from services.users_services import UserService
from core.deps import RoleChecker

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    limit: int = 10, 
    offset: int = 0, 
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(RoleChecker(["admin"]))
):
    service = UserService(db)
    users = await service.get_users(offset=offset, limit=limit)
    return users
