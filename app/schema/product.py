from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator

class ProductBase(BaseModel):
    name: str
    price: float
    special_price: Optional[float] = None
    stock: int
    category: str
    description: str
    images: List[str] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    special_price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None

class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator('images', mode='before')
    @classmethod
    def serialize_images(cls, v):
        if isinstance(v, list):
            return [img.url if hasattr(img, 'url') else img for img in v]
        return v
