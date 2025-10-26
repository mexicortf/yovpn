"""
Caching utilities with Redis integration
Provides connection pooling and optimized caching strategies
"""
import json
import logging
from typing import Optional, Any
from functools import wraps
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache manager with connection pooling
    """
    
    def __init__(self):
        self.pool: Optional[redis.ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection pool"""
        try:
            self.pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_pool_max_connections,
                socket_timeout=settings.redis_pool_timeout,
                socket_connect_timeout=5,
                decode_responses=True
            )
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            logger.info("✅ Redis connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.client = None
    
    async def close(self):
        """Close Redis connection pool"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("✅ Redis connection pool closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"❌ Redis get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"❌ Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Redis exists error for key {key}: {e}")
            return False


# Global cache instance
cache = RedisCache()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(arg) for arg in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"✅ Cache hit for {cache_key}")
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(cache_key, result, ttl)
                logger.debug(f"💾 Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator
