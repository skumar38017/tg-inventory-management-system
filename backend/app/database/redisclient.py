# backend/app/database/redisclient.py
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.config import REDIS_URL

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Connection pool for Redis
_redis_pool: Optional[aioredis.ConnectionPool] = None
_redis_client: Optional[aioredis.Redis] = None

async def init_redis() -> None:
    """Initialize Redis connection pool (call this at startup)"""
    global _redis_pool, _redis_client
    if _redis_pool is None:
        try:
            logger.info(f"Initializing Redis connection pool with URL: {REDIS_URL}")
            _redis_pool = aioredis.ConnectionPool.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                max_connections=10,
                health_check_interval=30
            )
            # Create a default client instance
            _redis_client = aioredis.Redis(connection_pool=_redis_pool)
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

async def get_redis() -> aioredis.Redis:
    """Get the Redis client instance"""
    if _redis_client is None:
        await init_redis()
    if _redis_client is None:  # Double check after initialization
        raise RuntimeError("Redis client not initialized")
    return _redis_client

@asynccontextmanager
async def redis_connection() -> AsyncGenerator[aioredis.Redis, None]:
    """Async context manager for Redis connections"""
    redis = await get_redis()
    try:
        yield redis
    except RedisError as e:
        logger.error(f"Redis operation failed: {e}")
        raise
    # Note: We don't close the client here as it's long-lived

async def check_redis_connectivity() -> bool:
    """Check if Redis is reachable"""
    try:
        redis = await get_redis()
        return await redis.ping()
    except Exception as e:
        logger.error(f"Redis connectivity check failed: {e}")
        return False

async def check_redis_connectivity_with_retry(
    retries: int = 3, 
    delay: float = 5
) -> bool:
    """Check Redis connectivity with retry logic"""
    for attempt in range(1, retries + 1):
        try:
            if await check_redis_connectivity():
                logger.info("Redis connection successful")
                return True
        except Exception as e:
            logger.warning(f"Connection attempt {attempt}/{retries} failed: {e}")
        
        if attempt < retries:
            logger.info(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
    
    logger.error("All Redis connection attempts failed")
    return False

async def close_redis() -> None:
    """Cleanup Redis connections (call this at shutdown)"""
    global _redis_pool, _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
    if _redis_pool is not None:
        await _redis_pool.disconnect()
        _redis_pool = None
    logger.info("Redis connections closed")

# For FastAPI dependency injection
async def get_redis_dependency() -> AsyncGenerator[aioredis.Redis, None]:
    """FastAPI dependency for Redis"""
    redis = await get_redis()
    try:
        yield redis
    finally:
        # Don't close the client here as it's long-lived
        pass