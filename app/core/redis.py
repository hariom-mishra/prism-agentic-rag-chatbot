import redis.asyncio as aioredis
from core.config import setting
from typing import Optional

redis_client: Optional[aioredis.Redis] = None

async def init_redis() -> Optional[aioredis.Redis]:
    """
    Initializes the Redis async client and pings the server to ensure connectivity.
    """
    global redis_client
    try:
        redis_client = aioredis.Redis(
            host=setting.REDIS_HOST,
            port=setting.REDIS_PORT,
            db=setting.REDIS_DB,
            decode_responses=True
        )
        # Test connection
        await redis_client.ping()
        print("🎉 Redis connected successfully on startup!")
        return redis_client
    except Exception as e:
        print(f"❌ Redis connection failed on startup: {e}")
        redis_client = None
        return None

async def close_redis():
    """
    Closes the Redis client connection pool on application shutdown.
    """
    global redis_client
    if redis_client is not None:
        try:
            await redis_client.aclose()
            print("🔌 Redis connection closed successfully.")
        except Exception as e:
            print(f"❌ Error closing Redis connection: {e}")
        finally:
            redis_client = None
