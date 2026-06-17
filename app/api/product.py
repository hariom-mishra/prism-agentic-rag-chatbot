from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from schema.product import ProductCreate, ProductResponse, ProductUpdate
from services.products_services import ProductServices
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db

router = APIRouter(prefix="/products", tags=["product"])

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
    id: Optional[int] = None,
    category: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    service = ProductServices(db=db)
    products = await service.get_products(limit=limit, offset=offset, id=id, category=category)
    return products

@router.get("/{id}", response_model=ProductResponse)
async def get_product_by_id(id: int, db: AsyncSession = Depends(get_db)):
    service = ProductServices(db=db)
    product = await service.get_product_by_id(product_id=id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
        )
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    service = ProductServices(db=db)
    new_product = await service.create_product(product_data=product)
    return new_product

@router.put("/{id}", response_model=ProductResponse)
async def update_product(id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    service = ProductServices(db=db)
    updated_product = await service.update_product(product_id=id, product_data=product)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
        )
    return updated_product

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    service = ProductServices(db=db)
    deleted = await service.delete_product(product_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
        )
    return {"message": f"Product with id {id} deleted successfully"}
