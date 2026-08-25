import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("varisetu.redis")

class RedisClient:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._memory_cache: dict = {}
        self.is_connected: bool = False

    async def connect(self):
        """Attempt to connect to Redis, fall back to in-memory mode if unavailable."""
        if not settings.REDIS_URL:
            logger.info("No REDIS_URL configured; using in-memory cache fallback.")
            return

        try:
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0
            )
            await self.redis.ping()
            self.is_connected = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self.is_connected = False
            self.redis = None
            logger.warning(f"Redis connection failed ({e}); operating in in-memory cache fallback mode.")

    async def disconnect(self):
        if self.redis and self.is_connected:
            await self.redis.close()
            self.is_connected = False
            logger.info("Disconnected from Redis.")

    async def get(self, key: str) -> Optional[Any]:
        if self.is_connected and self.redis:
            try:
                val = await self.redis.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        return self._memory_cache.get(key)

    async def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        serialized = json.dumps(value, default=str)
        if self.is_connected and self.redis:
            try:
                await self.redis.set(key, serialized, ex=expire_seconds)
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        self._memory_cache[key] = value
        return True

    async def delete(self, key: str) -> bool:
        if self.is_connected and self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        self._memory_cache.pop(key, None)
        return True

    async def publish(self, channel: str, message: dict):
        serialized = json.dumps(message, default=str)
        if self.is_connected and self.redis:
            try:
                await self.redis.publish(channel, serialized)
            except Exception as e:
                logger.error(f"Redis publish error: {e}")


redis_client = RedisClient()
