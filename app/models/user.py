from core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime, timezone
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column( String(255), nullable=False, unique=True, index=True)
    role: Mapped[str]= mapped_column(String(50), default="user", nullable=False)
    gender: Mapped[str]= mapped_column(String(10), nullable=True)
    pincode: Mapped[str]=mapped_column(String(6), nullable=True)
    hashed_password: Mapped[str]=mapped_column(String(255), nullable=False, )
    created_at: Mapped[datetime]=mapped_column(
        server_default=func.now(),
        default=datetime.now(timezone.utc)
    )