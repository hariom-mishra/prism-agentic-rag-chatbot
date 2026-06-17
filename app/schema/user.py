from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    gender: Optional[str] = None
    pincode: Optional[str] = None

class UserSignUp(UserBase):
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserRoleUpdate(BaseModel):
    role: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    pincode: Optional[str] = None
    password: Optional[str] = None
