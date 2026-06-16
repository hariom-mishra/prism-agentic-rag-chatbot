from typing import List
from pydantic import BaseModel, ConfigDict

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




    
