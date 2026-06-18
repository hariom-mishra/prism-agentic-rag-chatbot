import json
import logging
from typing import Any, Optional
from core import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class CacheService:
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        Gets a deserialized JSON value from Redis.
        If Redis is unavailable or fails, returns None and logs the error.
        """
        if redis.redis_client is None:
            return None
        try:
            data = await redis.redis_client.get(key)
            if data:
                return json.loads(data)
        except RedisError as e:
            logger.error(f"Redis GET failed for key '{key}': {e}", exc_info=True)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to deserialize cache data for key '{key}': {e}", exc_info=True)
        return None

    @staticmethod
    async def set(key: str, value: Any, expire: int = 3600) -> bool:
        """
        Serializes and sets a value in Redis with an optional TTL (in seconds).
        If Redis is unavailable or fails, returns False and logs the error.
        """
        if redis.redis_client is None:
            return False
        try:
            serialized = json.dumps(value)
            await redis.redis_client.set(key, serialized, ex=expire)
            return True
        except RedisError as e:
            logger.error(f"Redis SET failed for key '{key}': {e}", exc_info=True)
        except TypeError as e:
            logger.error(f"Failed to serialize value for key '{key}': {e}", exc_info=True)
        return False

    @staticmethod
    async def delete(key: str) -> bool:
        """
        Deletes a key from Redis.
        If Redis is unavailable or fails, returns False and logs the error.
        """
        if redis.redis_client is None:
            return False
        try:
            await redis.redis_client.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Redis DELETE failed for key '{key}': {e}", exc_info=True)
        return False

    @staticmethod
    async def delete_pattern(pattern: str) -> bool:
        """
        Deletes all keys matching the given pattern using non-blocking SCAN.
        If Redis is unavailable or fails, returns False and logs the error.
        """
        if redis.redis_client is None:
            return False
        try:
            cursor = 0
            deleted_count = 0
            while True:
                cursor, keys = await redis.redis_client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    await redis.redis_client.delete(*keys)
                    deleted_count += len(keys)
                if cursor == 0:
                    break
            logger.info(f"Redis deleted {deleted_count} keys matching pattern '{pattern}'")
            return True
        except RedisError as e:
            logger.error(f"Redis scan/delete failed for pattern '{pattern}': {e}", exc_info=True)
        return False
