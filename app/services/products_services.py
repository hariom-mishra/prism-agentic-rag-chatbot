from repository.products_repo import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class ProductServices:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)

    async def get_products(self, limit: int, offset: int, id: Optional[int] = None, category: Optional[str] = None):
        return await self.repo.get_products(limit=limit, offset=offset, id=id, category=category)

    async def get_product_by_id(self, product_id: int):
        return await self.repo.get_product_by_id(product_id)

    async def create_product(self, product_data):
        return await self.repo.create_product(product_data)

    async def update_product(self, product_id: int, product_data):
        return await self.repo.update_product(product_id, product_data)

    async def delete_product(self, product_id: int):
        return await self.repo.delete_product(product_id)