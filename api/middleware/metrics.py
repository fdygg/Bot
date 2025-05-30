from fastapi import Request
import time
from datetime import datetime, UTC

class MetricsMiddleware:
    def __init__(self):
        self.requests_count = 0
        self.total_response_time = 0

    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        self.requests_count += 1

        response = await call_next(request)
        
        process_time = time.time() - start_time
        self.total_response_time += process_time
        
        # Add metrics headers
        response.headers["X-Response-Time"] = str(process_time)
        response.headers["X-Request-ID"] = str(request.state.request_id)
        
        return response