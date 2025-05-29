from fastapi import Request, Response
from datetime import datetime, timedelta
import logging
from typing import Optional, Any
import redis
import json

from ..config import config

logger = logging.getLogger(__name__)

class CacheMiddleware:
    """Middleware for response caching"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB
        )
        self.default_ttl = config.CACHE_TTL

    async def __call__(self, request: Request, call_next):
        if request.method != "GET":
            return await call_next(request)
            
        try:
            # Get cache key
            cache_key = await get_cache_key(request)
            
            # Try to get from cache
            cached_response = await get_cache(
                self.redis_client,
                cache_key
            )
            
            if cached_response:
                return Response(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers=cached_response["headers"],
                    media_type=cached_response["media_type"]
                )
            
            # Get fresh response
            response = await call_next(request)
            
            # Cache the response
            await set_cache(
                self.redis_client,
                cache_key,
                {
                    "content": response.body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type
                },
                self.default_ttl
            )
            
            return response
            
        except Exception as e:
            logger.error(f"""
            Cache middleware error:
            Error: {str(e)}
            Time: 2025-05-28 15:44:14 UTC
            User: fdygg
            """)
            return await call_next(request)

async def get_cache_key(request: Request) -> str:
    """Generate cache key from request"""
    return f"cache:{request.url.path}:{request.query_params}"

async def get_cache(
    redis_client: redis.Redis,
    key: str
) -> Optional[dict]:
    """Get cached response"""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except:
        return None

async def set_cache(
    redis_client: redis.Redis,
    key: str,
    value: dict,
    ttl: int
):
    """Set cached response"""
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    except Exception as e:
        logger.error(f"""
        Cache set error:
        Key: {key}
        Error: {str(e)}
        Time: 2025-05-28 15:44:14 UTC
        User: fdygg
        """)

async def clear_cache(
    redis_client: redis.Redis,
    pattern: str = "*"
):
    """Clear cache entries matching pattern"""
    try:
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
    except Exception as e:
        logger.error(f"""
        Cache clear error:
        Pattern: {pattern}
        Error: {str(e)}
        Time: 2025-05-28 15:44:14 UTC
        User: fdygg
        """)