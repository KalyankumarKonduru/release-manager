"""
Redis connection management and caching utilities.

This module provides:
- Redis connection pool management
- Cache get/set/invalidate operations
- Async context manager for connection lifecycle
"""

import json
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings


class RedisManager:
    """
    Manages Redis connection and caching operations.

    This class handles:
    - Connection pool initialization and cleanup
    - Async cache operations (get, set, delete)
    - Cache key management with namespacing
    - Error handling and fallback behavior
    """

    def __init__(self):
        """Initialize Redis manager."""
        self._redis: Optional[Redis] = None

    async def initialize(self) -> None:
        """
        Initialize Redis connection pool.

        Raises:
            RuntimeError: If connection fails
        """
        try:
            self._redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={},
            )
            # Test connection
            await self._redis.ping()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Redis: {str(e)}")

    async def close(self) -> None:
        """
        Close Redis connection pool.

        Raises:
            RuntimeError: If closing fails
        """
        if self._redis is None:
            return

        try:
            await self._redis.close()
        except Exception as e:
            raise RuntimeError(f"Failed to close Redis: {str(e)}")

    def _get_key(self, namespace: str, key: str) -> str:
        """
        Generate a namespaced cache key.

        Args:
            namespace: Cache namespace/prefix
            key: Cache key

        Returns:
            Fully qualified cache key
        """
        return f"{namespace}:{key}"

    async def get_cache(
        self,
        key: str,
        namespace: str = "app",
    ) -> Optional[Any]:
        """
        Retrieve a value from cache.

        Args:
            key: Cache key to retrieve
            namespace: Cache namespace (default: "app")

        Returns:
            Cached value if exists and is valid JSON, None otherwise
        """
        if self._redis is None:
            return None

        try:
            full_key = self._get_key(namespace, key)
            value = await self._redis.get(full_key)

            if value is None:
                return None

            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception:
            return None

    async def set_cache(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "app",
    ) -> bool:
        """
        Store a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 300)
            namespace: Cache namespace (default: "app")

        Returns:
            True if successful, False otherwise
        """
        if self._redis is None:
            return False

        try:
            full_key = self._get_key(namespace, key)
            ttl = ttl or settings.REDIS_TIMEOUT

            # Serialize value to JSON if it's a complex type
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = value

            await self._redis.setex(full_key, ttl, serialized_value)
            return True
        except Exception:
            return False

    async def delete_cache(
        self,
        key: str,
        namespace: str = "app",
    ) -> bool:
        """
        Delete a value from cache.

        Args:
            key: Cache key to delete
            namespace: Cache namespace (default: "app")

        Returns:
            True if key existed and was deleted, False otherwise
        """
        if self._redis is None:
            return False

        try:
            full_key = self._get_key(namespace, key)
            result = await self._redis.delete(full_key)
            return result > 0
        except Exception:
            return False

    async def invalidate_cache(
        self,
        pattern: str,
        namespace: str = "app",
    ) -> int:
        """
        Invalidate all keys matching a pattern.

        Args:
            pattern: Pattern to match (supports * wildcard)
            namespace: Cache namespace (default: "app")

        Returns:
            Number of keys deleted
        """
        if self._redis is None:
            return 0

        try:
            full_pattern = self._get_key(namespace, pattern)
            # Use SCAN for safe pattern matching with large keysets
            cursor = 0
            deleted_count = 0

            while True:
                cursor, keys = await self._redis.scan(
                    cursor,
                    match=full_pattern,
                    count=100,
                )

                if keys:
                    deleted_count += await self._redis.delete(*keys)

                if cursor == 0:
                    break

            return deleted_count
        except Exception:
            return 0

    async def exists(
        self,
        key: str,
        namespace: str = "app",
    ) -> bool:
        """
        Check if a key exists in cache.

        Args:
            key: Cache key to check
            namespace: Cache namespace (default: "app")

        Returns:
            True if key exists, False otherwise
        """
        if self._redis is None:
            return False

        try:
            full_key = self._get_key(namespace, key)
            result = await self._redis.exists(full_key)
            return result > 0
        except Exception:
            return False

    async def increment(
        self,
        key: str,
        amount: int = 1,
        namespace: str = "app",
    ) -> Optional[int]:
        """
        Increment a numeric value in cache.

        Args:
            key: Cache key
            amount: Amount to increment (default: 1)
            namespace: Cache namespace (default: "app")

        Returns:
            New value if successful, None otherwise
        """
        if self._redis is None:
            return None

        try:
            full_key = self._get_key(namespace, key)
            result = await self._redis.incrby(full_key, amount)
            return result
        except Exception:
            return None

    async def health_check(self) -> bool:
        """
        Check Redis connection health.

        Returns:
            True if Redis is responding, False otherwise
        """
        if self._redis is None:
            return False

        try:
            await self._redis.ping()
            return True
        except Exception:
            return False


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> Optional[Redis]:
    """
    Dependency to get Redis client.

    Returns:
        Redis client if initialized, None otherwise
    """
    return redis_manager._redis
