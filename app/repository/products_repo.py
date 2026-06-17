from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.product import Product
from models.image import Image
from typing import Optional

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_products(self, limit: int, offset: int, id: Optional[int] = None, category: Optional[str] = None):
        query = select(Product).options(selectinload(Product.images)).offset(offset).limit(limit)
        if id:
            query = query.where(Product.id == id)
        if category:
            query = query.where(Product.category == category)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_product_by_id(self, product_id: int):
        query = select(Product).options(selectinload(Product.images)).where(Product.id == product_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_product(self, product_data):
        product_model = Product(
            name=product_data.name,
            price=product_data.price,
            special_price=product_data.special_price,
            stock=product_data.stock,
            category=product_data.category,
            description=product_data.description
        )
        if product_data.images:
            product_model.images = [Image(url=url) for url in product_data.images]
        
        self.db.add(product_model)
        await self.db.commit()
        return await self.get_product_by_id(product_model.id)

    async def update_product(self, product_id: int, product_data):
        product_model = await self.get_product_by_id(product_id)
        if not product_model:
            return None
        
        for field in ["name", "price", "special_price", "stock", "category", "description"]:
            value = getattr(product_data, field, None)
            if value is not None:
                setattr(product_model, field, value)
        
        if product_data.images is not None:
            product_model.images.clear()
            product_model.images.extend([Image(url=url) for url in product_data.images])
            
        await self.db.commit()
        return await self.get_product_by_id(product_model.id)

    async def delete_product(self, product_id: int):
        product_model = await self.get_product_by_id(product_id)
        if not product_model:
            return False
        
        await self.db.delete(product_model)
        await self.db.commit()
        return True