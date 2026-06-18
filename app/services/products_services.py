from repository.products_repo import ProductRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from schema.product import ProductResponse
from services.cache_service import CacheService

class ProductServices:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)

    async def get_products(self, limit: int, offset: int, id: Optional[int] = None, category: Optional[str] = None):
        """
        Gets products from cache if available, otherwise queries database and caches the results.
        """
        # Formulate a deterministic cache key for listing with filters
        cache_key = f"products:list:limit={limit}:offset={offset}:id={id or ''}:category={category or ''}"
        
        cached_list = await CacheService.get(cache_key)
        if cached_list is not None:
            return cached_list

        products = await self.repo.get_products(limit=limit, offset=offset, id=id, category=category)
        
        # Serialize database models to list of dictionary items using Pydantic model
        serialized_products = [
            ProductResponse.model_validate(p).model_dump() for p in products
        ]
        
        # Cache list results for 1 hour (3600 seconds)
        await CacheService.set(cache_key, serialized_products, expire=3600)
        return serialized_products

    async def get_product_by_id(self, product_id: int):
        """
        Gets a product by ID from cache if available, otherwise queries database and caches it.
        """
        cache_key = f"product:{product_id}"
        
        cached_product = await CacheService.get(cache_key)
        if cached_product is not None:
            return cached_product

        product = await self.repo.get_product_by_id(product_id)
        if product:
            # Serialize model using Pydantic schema
            serialized_product = ProductResponse.model_validate(product).model_dump()
            await CacheService.set(cache_key, serialized_product, expire=3600)
            return serialized_product
            
        return None

    async def create_product(self, product_data):
        """
        Creates a new product and invalidates all product list caches.
        """
        new_product = await self.repo.create_product(product_data)
        if new_product:
            # Invalidate all listing caches since they contain stale products list
            await CacheService.delete_pattern("products:list:*")
            return ProductResponse.model_validate(new_product).model_dump()
        return None

    async def update_product(self, product_id: int, product_data):
        """
        Updates an existing product and invalidates both its specific cache and list caches.
        """
        updated_product = await self.repo.update_product(product_id, product_data)
        if updated_product:
            # Invalidate individual and listing caches
            await CacheService.delete(f"product:{product_id}")
            await CacheService.delete_pattern("products:list:*")
            return ProductResponse.model_validate(updated_product).model_dump()
        return None

    async def delete_product(self, product_id: int):
        """
        Deletes a product and invalidates its specific cache and list caches.
        """
        deleted = await self.repo.delete_product(product_id)
        if deleted:
            # Invalidate individual and listing caches
            await CacheService.delete(f"product:{product_id}")
            await CacheService.delete_pattern("products:list:*")
        return deleted