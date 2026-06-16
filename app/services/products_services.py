from repository.products_repo import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession

class ProductServices:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)

    async def get_products(self, limit: int, offset: int, id: int = None):
        products = await self.repo.get_products(limit, offset, id)
        return products
        


    
    
    