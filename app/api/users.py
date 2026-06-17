from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schema.user import UserResponse, UserRoleUpdate, UserUpdate
from services.users_services import UserService
from core.deps import RoleChecker, get_current_user
from models.user import User

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

@router.put("/me", response_model=UserResponse)
async def update_my_details(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    updated_user = await service.update_user_details(user_id=current_user.id, user_update=user_update)
    return updated_user

@router.put("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(RoleChecker(["admin"]))
):
    service = UserService(db)
    updated_user = await service.change_user_role(user_id=user_id, role=role_update.role)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user
