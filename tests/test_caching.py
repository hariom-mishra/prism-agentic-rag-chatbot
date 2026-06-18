import pytest
import redis
import json
from httpx import AsyncClient
from core.config import setting

# Run all tests in this file with anyio (async)
pytestmark = pytest.mark.anyio

def get_redis_client():
    return redis.Redis(
        host=setting.REDIS_HOST,
        port=setting.REDIS_PORT,
        db=setting.REDIS_DB,
        decode_responses=True
    )

async def test_caching_and_invalidation_flow(client: AsyncClient):
    r = get_redis_client()
    
    # Ensure cache starts clean
    r.flushdb()

    # 1. Create a product
    product_payload = {
        "name": "Cached Phone",
        "price": 499.99,
        "special_price": 449.99,
        "stock": 100,
        "category": "Electronics",
        "description": "A phone to test caching.",
        "images": ["phone1.png"]
    }
    response = await client.post("/products/", json=product_payload)
    assert response.status_code == 201
    product = response.json()
    product_id = product["id"]

    # Since a write occurred, any list cache should have been invalidated.
    # No list keys should exist yet because we haven't read them.
    assert len(r.keys("products:list:*")) == 0
    assert not r.exists(f"product:{product_id}")

    # 2. Get product list (this should populate list cache)
    list_res = await client.get("/products/")
    assert list_res.status_code == 200
    
    # Check that list cache key is now populated in Redis
    list_keys = r.keys("products:list:*")
    assert len(list_keys) == 1
    cached_list = json.loads(r.get(list_keys[0]))
    assert len(cached_list) == 1
    assert cached_list[0]["id"] == product_id

    # 3. Get product by ID (this should populate individual product cache)
    detail_res = await client.get(f"/products/{product_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["name"] == "Cached Phone"

    # Check that individual product cache key is now populated in Redis
    product_cache_key = f"product:{product_id}"
    assert r.exists(product_cache_key)
    cached_product = json.loads(r.get(product_cache_key))
    assert cached_product["name"] == "Cached Phone"
    assert cached_product["price"] == 499.99

    # 4. Modify the cache directly to verify the app reads from cache (Cache Hit assertion)
    cached_product["name"] = "Hacked Cached Phone"
    r.set(product_cache_key, json.dumps(cached_product))

    # Read again - the endpoint should return the hacked name from the cache
    hit_res = await client.get(f"/products/{product_id}")
    assert hit_res.status_code == 200
    assert hit_res.json()["name"] == "Hacked Cached Phone"

    # 5. Update the product (this should invalidate both the specific cache and list cache)
    update_payload = {
        "name": "Updated Cached Phone",
        "price": 520.00
    }
    update_res = await client.put(f"/products/{product_id}", json=update_payload)
    assert update_res.status_code == 200

    # Assert that the specific cache key and listing cache keys were deleted/invalidated
    assert not r.exists(product_cache_key)
    assert len(r.keys("products:list:*")) == 0

    # 6. Fetch from DB again to verify new value is cached (re-population)
    refetch_res = await client.get(f"/products/{product_id}")
    assert refetch_res.status_code == 200
    assert refetch_res.json()["name"] == "Updated Cached Phone"
    assert r.exists(product_cache_key)

    # 7. Delete the product (this should invalidate the cache again)
    delete_res = await client.delete(f"/products/{product_id}")
    assert delete_res.status_code == 200
    
    assert not r.exists(product_cache_key)
    assert len(r.keys("products:list:*")) == 0

    r.close()
