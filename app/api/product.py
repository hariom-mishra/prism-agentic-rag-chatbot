from fastapi import APIRouter
from typing import Optional, List
from schema.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["product"])

@router.get("/", response_model=List[ProductResponse])
def get_products(id: Optional[int] = None, limit:Optional[int] = 10, offset: Optional[int]=0):
    return [
        ProductResponse(id=1, name="product1", images=["image1", "image2"]),
        ProductResponse(id=2, name="product2", images=["image1", "image2"]),
        ProductResponse(id=3, name="product3", images=["image1", "image2"]),
        ProductResponse(id=4, name="product4", images=["image1", "image2"]),
    ]

@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate):
    return ProductResponse(id=1, name="product1", images=["image1", "image2"])

@router.put("/{id}", response_model=ProductResponse)
def update_product(id: int, product: ProductUpdate):
    return ProductResponse(id=1, name="product1", images=["image1", "image2"])


