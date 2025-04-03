# backend/app/database/redisclient.py
import redis
from backend.app.config import REDIS_URL  # Import REDIS_URL from config
from redis.exceptions import RedisError
import time
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.entry_inventory_model import EntryInventory
from backend.app.schema.entry_inventory_schema import (
    InventoryRedisOut,
    StoreInventoryRedis
)
from redis import asyncio as aioredis
import json
import os


# Set up logging to display info and error messages
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a Redis connection using the URL from the config
# Initialize Redis client
try:
    logger.info(f"Initializing Redis client with URL: {REDIS_URL}")
    redis_client = aioredis.from_url(
        REDIS_URL,  
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {e}")
    raise

def get_redis_client():
    """Returns the Redis client instance."""
    logger.debug("Returning Redis client instance.")
    return redis_client

# Check Redis Connectivity
def check_redis_connectivity():
    """Check Redis connectivity asynchronously."""
    try:
        logger.info("Pinging Redis server to check connectivity...")
        # Ping the Redis server to check if it's available
        if redis_client.ping():
            logger.info("Redis is connected.")
            return True
    except RedisError as e:
        logger.error(f"Redis connection failed: {e}")
        return False

# Optional: Retry mechanism for Redis connectivity check
def check_redis_connectivity_with_retry(retries=3, delay=5):
    """Check Redis connectivity with retries."""
    attempt = 0
    while attempt < retries:
        try:
            logger.info(f"Attempting to ping Redis server... (Attempt {attempt + 1}/{retries})")
            # Ping the Redis server to check if it's available
            if redis_client.ping():
                logger.info("Redis is connected.")
                return True
        except RedisError as e:
            logger.error(f"Redis connection failed on attempt {attempt + 1}: {e}")
            attempt += 1
            logger.info(f"Retrying in {delay} seconds... ({attempt}/{retries})")
            time.sleep(delay)
    logger.error("Redis connection failed after all retries.")
    return False

