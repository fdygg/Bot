from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
import redis

from ..config import config

logger = logging.getLogger(__name__)

class RateLimitingMiddleware:
    """Middleware for rate limiting requests"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB
        )
        self.rate_limit = config.RATE_LIMIT
        self.rate_limit_window = config.RATE_LIMIT_WINDOW

    async def __call__(self, request: Request, call_next):
        try:
            key = await get_rate_limit_key(request)
            
            # Check rate limit
            if not await check_rate_limit(self.redis_client, key, self.rate_limit):
                logger.warning(f"""
                Rate limit exceeded:
                IP: {request.client.host}
                Path: {request.url.path}
                Time: 2025-05-28 15:44:14 UTC
                User: fdygg
                """)
                
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "Too many requests",
                        "type": "RateLimitExceeded",
                        "timestamp": "2025-05-28 15:44:14"
                    }
                )
            
            # Update rate limit counter
            await update_rate_limit(
                self.redis_client,
                key,
                self.rate_limit_window
            )
            
            return await call_next(request)
            
        except redis.RedisError as e:
            logger.error(f"""
            Rate limiting error:
            Error: {str(e)}
            Time: 2025-05-28 15:44:14 UTC
            User: fdygg
            """)
            return await call_next(request)

async def get_rate_limit_key(request: Request) -> str:
    """Generate rate limit key based on IP and path"""
    return f"rate_limit:{request.client.host}:{request.url.path}"

async def check_rate_limit(
    redis_client: redis.Redis,
    key: str,
    limit: int
) -> bool:
    """Check if rate limit is exceeded"""
    count = redis_client.get(key)
    return not count or int(count) < limit

async def update_rate_limit(
    redis_client: redis.Redis,
    key: str,
    window: int
):
    """Update rate limit counter"""
    pipeline = redis_client.pipeline()
    pipeline.incr(key)
    pipeline.expire(key, window)
    pipeline.execute()