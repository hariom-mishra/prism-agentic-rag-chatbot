from sqlalchemy.ext.asyncio import AsyncSession
from repository.users_repo import UserRepository
from schema.user import UserSignUp
from core.security import verify_password
from models.user import User
from fastapi import HTTPException

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self, user: UserSignUp) -> User:
        # Check if the email is already registered, if yes reject request with status code 400 Bad Request
        res_user = await self.repo.get_user_by_email(user.email)
        if res_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        return await self.repo.create_user(user)

    async def login_user(self, email: str, password: str) -> User:
        # Check if the email is registered, if not reject request with status code 404 Not Found
        res_user = await self.repo.get_user_by_email(email=email)
        if not res_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if the password is correct, if not reject request with status code 401 Unauthorized
        if not verify_password(password, res_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")
       
        return res_user

    async def get_users(self, offset: int, limit: int) -> list[User]:
        return await self.repo.get_users(offset, limit)
