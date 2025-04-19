# backend/app/dependencies.py

from backend.app.database.redisclient import get_redis

async def get_redis_client():
    redis = await get_redis()
    try:
        yield redis
    finally:
        await redis.close()