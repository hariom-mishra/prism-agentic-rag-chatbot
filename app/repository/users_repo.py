from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.security import hash_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user):
        user_model = User(
            name=user.name,
            email=user.email,
            hashed_password=hash_password(user.password),
            gender=user.gender,
            pincode=user.pincode
        )
        self.db.add(user_model)
        await self.db.commit()
        await self.db.refresh(user_model)
        return user_model

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_users(self, offset: int, limit: int):
        result = await self.db.execute(select(User).offset(offset).limit(limit))
        return result.scalars().all()

    async def soft_delete_user(self, user_id: int):
        pass
    
    async def update_user(self, user_id: int, user_data):
        pass