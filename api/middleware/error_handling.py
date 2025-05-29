from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Union, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """Middleware for handling various types of errors"""
    
    async def __call__(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as exc:
            return await handle_http_exception(request, exc)
        except ValidationError as exc:
            return await handle_validation_error(request, exc)
        except Exception as exc:
            return await handle_database_error(request, exc)

async def handle_http_exception(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.error(f"""
    HTTP Exception:
    Status: {exc.status_code}
    Detail: {exc.detail}
    Path: {request.url.path}
    Time: 2025-05-28 15:44:14 UTC
    User: fdygg
    """)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "HTTPException",
            "timestamp": "2025-05-28 15:44:14",
            "path": request.url.path
        }
    )

async def handle_validation_error(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """Handle validation errors"""
    logger.error(f"""
    Validation Error:
    Errors: {exc.errors()}
    Path: {request.url.path}
    Time: 2025-05-28 15:44:14 UTC
    User: fdygg
    """)
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "type": "ValidationError",
            "timestamp": "2025-05-28 15:44:14",
            "path": request.url.path
        }
    )

async def handle_database_error(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle database errors"""
    logger.error(f"""
    Database Error:
    Error: {str(exc)}
    Path: {request.url.path}
    Time: 2025-05-28 15:44:14 UTC
    User: fdygg
    """)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "DatabaseError",
            "timestamp": "2025-05-28 15:44:14",
            "path": request.url.path
        }
    )