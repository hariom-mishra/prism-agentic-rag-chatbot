from fastapi import APIRouter
from typing import Optional, List
from schema.product import ProductCreate, ProductResponse, ProductUpdate
from services.products_services import ProductServices
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from fastapi import Depends

router = APIRouter(prefix="/products", tags=["product"])

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
     id: Optional[int] = None,
      limit:Optional[int] = 10, offset: Optional[int]=0):

    service = ProductServices(db=db)
    products = await service.get_products(limit, offset, id)
    return products

@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate):
    return ProductResponse(id=1, name="product1", images=["image1", "image2"])

@router.put("/{id}", response_model=ProductResponse)
def update_product(id: int, product: ProductUpdate):
    return ProductResponse(id=1, name="product1", images=["image1", "image2"])


