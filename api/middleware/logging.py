from fastapi import Request, Response
import logging
import time
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """Middleware for logging requests and responses"""
    
    async def __call__(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Log request
        await log_request(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = round(time.time() - start_time, 3)
        
        # Log response
        await log_response(response, duration)
        
        return response

async def log_request(request: Request):
    """Log incoming request details"""
    try:
        log_data = await format_request_log(request)
        logger.info(f"""
        Request:
        {log_data}
        Time: 2025-05-28 15:44:14 UTC
        User: fdygg
        """)
    except Exception as e:
        logger.error(f"""
        Request logging error:
        Error: {str(e)}
        Time: 2025-05-28 15:44:14 UTC
        User: fdygg
        """)

async def log_response(response: Response, duration: float):
    """Log outgoing response details"""
    try:
        log_data = format_response_log(response, duration)
        logger.info(f"""
        Response:
        {log_data}
        Duration: {duration}s
        Time: 2025-05-28 15:44:14 UTC
        User: fdygg
        """)
    except Exception as e:
        logger.error(f"""
        Response logging error:
        Error: {str(e)}
        Time: 2025-05-28 15:44:14 UTC
        User: fdygg
        """)

async def format_request_log(request: Request) -> Dict[str, Any]:
    """Format request data for logging"""
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None,
        "timestamp": "2025-05-28 15:44:14"
    }

def format_response_log(response: Response, duration: float) -> Dict[str, Any]:
    """Format response data for logging"""
    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "duration": duration,
        "timestamp": "2025-05-28 15:44:14"
    }