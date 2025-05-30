from fastapi import Request
from fastapi.middleware.gzip import GZipMiddleware
from typing import Optional

class CompressionMiddleware:
    def __init__(self, minimum_size: int = 500):
        self.minimum_size = minimum_size
        
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Compress jika response size > minimum_size
        if len(response.body) > self.minimum_size:
            # Implementasi kompresi
            pass
            
        return response