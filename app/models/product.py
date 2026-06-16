from core.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    images: Mapped[List["Image"]] = relationship(back_populates="product")

