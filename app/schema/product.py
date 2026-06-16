from typing import List
from pydantic import BaseModel, ConfigDict, field_validator

class ProductBase(BaseModel):
    name: str
    images: List[str]

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator('images', mode='before')
    @classmethod
    def serialize_images(cls, v):
        if isinstance(v, list):
            return [img.url if hasattr(img, 'url') else img for img in v]
        return v
