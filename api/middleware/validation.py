from fastapi import Request, HTTPException
from typing import Dict, Any

class ValidationMiddleware:
    async def __call__(self, request: Request, call_next):
        # Validasi sebelum request diproses
        await self.validate_request(request)
        
        response = await call_next(request)
        return response

    async def validate_request(self, request: Request):
        # Contoh validasi basic
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type")
            if not content_type or "application/json" not in content_type:
                raise HTTPException(
                    status_code=400,
                    detail="Content-Type must be application/json"
                )