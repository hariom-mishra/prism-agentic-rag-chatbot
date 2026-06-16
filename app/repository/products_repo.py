from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.product import Product

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_products(self, limit: int, offset: int, id: int = None):
        query = select(Product).offset(offset).limit(limit)
        if id:
            query = query.where(Product.id == id)
        result = await self.db.execute(query)
        print(f"result: {result}")
        return result.scalars().all()