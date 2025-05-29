from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import logging
from typing import Optional, Dict, Any

from ..config import config
from ..models.auth import TokenResponse

logger = logging.getLogger(__name__)
security = HTTPBearer()

class JWTAuthMiddleware:
    """JWT Authentication middleware"""
    
    def __init__(self):
        self.secret_key = config.JWT_SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM
        self.access_token_expire = config.JWT_ACCESS_TOKEN_EXPIRE
        self.refresh_token_expire = config.JWT_REFRESH_TOKEN_EXPIRE

    async def __call__(self, request: Request, call_next):
        if getattr(request.scope.get("endpoint", None), "skip_auth", False):
            return await call_next(request)
            
        try:
            token = await get_token_from_header(request)
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "message": "Not authenticated",
                        "type": "AuthenticationError",
                        "timestamp": "2025-05-28 15:44:14"
                    }
                )
                
            payload = decode_token(token, self.secret_key, self.algorithm)
            request.state.user = payload.get("sub", "fdygg")
            
            response = await call_next(request)
            return response
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": "Token expired",
                    "type": "TokenExpiredError",
                    "timestamp": "2025-05-28 15:44:14"
                }
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": "Invalid token",
                    "type": "InvalidTokenError",
                    "timestamp": "2025-05-28 15:44:14"
                }
            )
        except Exception as e:
            logger.error(f"""
            Auth middleware error:
            Error: {str(e)}
            Time: 2025-05-28 15:44:14 UTC
            User: fdygg
            """)
            raise HTTPException(status_code=500, detail="Internal server error")

async def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = decode_token(token, config.JWT_SECRET_KEY, config.JWT_ALGORITHM)
        if payload["type"] != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_access_token(
    username: str,
    expires_delta: Optional[timedelta] = None
) -> TokenResponse:
    """Create new access and refresh tokens"""
    
    # Access token
    access_expires = expires_delta or timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE)
    access_payload = {
        "sub": username,
        "type": "access",
        "iat": datetime.strptime("2025-05-28 15:44:14", "%Y-%m-%d %H:%M:%S"),
        "exp": datetime.strptime("2025-05-28 15:44:14", "%Y-%m-%d %H:%M:%S") + access_expires
    }
    access_token = jwt.encode(
        access_payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )
    
    # Refresh token
    refresh_expires = timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRE)
    refresh_payload = {
        "sub": username,
        "type": "refresh",
        "iat": datetime.strptime("2025-05-28 15:44:14", "%Y-%m-%d %H:%M:%S"),
        "exp": datetime.strptime("2025-05-28 15:44:14", "%Y-%m-%d %H:%M:%S") + refresh_expires
    }
    refresh_token = jwt.encode(
        refresh_payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

def decode_token(token: str, secret_key: str, algorithm: str) -> Dict[str, Any]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={
                "message": "Token expired",
                "type": "TokenExpiredError",
                "timestamp": "2025-05-28 15:44:14"
            }
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail={
                "message": "Invalid token",
                "type": "InvalidTokenError",
                "timestamp": "2025-05-28 15:44:14"
            }
        )

async def get_token_from_header(request: Request) -> Optional[str]:
    """Extract token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
        
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None