from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: dict):
        user_model = User(
            name=user_data.get("name"),
            email=user_data.get("email"),
            hashed_password=user_data.get("hashed_password"),
            gender=user_data.get("gender"),
            pincode=user_data.get("pincode"),
            role=user_data.get("role", "user")
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
    
    async def update_user(self, user_id: int, user_data: dict):
        result = await self.db.execute(select(User).where(User.id == user_id))
        user_model = result.scalars().first()
        if not user_model:
            return None
        for key, value in user_data.items():
            if value is not None:
                setattr(user_model, key, value)
        await self.db.commit()
        await self.db.refresh(user_model)
        return user_model