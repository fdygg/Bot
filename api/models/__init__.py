from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

# Base configuration
CURRENT_TIMESTAMP = "2025-05-28 15:40:52"
CURRENT_USER = "fdygg"

# Import all models
from .auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    AdminLoginRequest,
    RefreshTokenRequest,
    PasswordResetRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest
)

from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserRole,
    UserStatus
)

from .product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductFilter
)

from .stock import (
    StockResponse,
    StockItem,
    StockAddRequest,
    StockReduceRequest,
    StockHistoryResponse,
    StockFilter
)

from .transaction import (
    TransactionResponse,
    TransactionCreate,
    TransactionFilter,
    TransactionType,
    TransactionStatus
)

from .balance import (
    BalanceResponse,
    BalanceUpdateRequest,
    BalanceHistoryResponse,
    BalanceFilter,
    BalanceType
)

from .dashboard import (
    SystemInfo,
    UserActivity,
    SystemStatus,
    UserStats,
    StockAlert,
    DashboardStats,
    UserDashboard,
    DashboardSettings
)

from .admin import (
    AdminStats,
    AdminDashboard,
    SystemInfo,
    UserActivity
)

# Common base models
class BaseTimestampModel(BaseModel):
    """Base model with timestamp"""
    created_at: datetime = Field(default_factory=lambda: datetime.strptime(CURRENT_TIMESTAMP, "%Y-%m-%d %H:%M:%S"))
    updated_at: Optional[datetime] = None
    created_by: str = CURRENT_USER
    updated_by: Optional[str] = None

class BaseStatusModel(BaseModel):
    """Base model with status"""
    is_active: bool = True
    status: str = "active"
    status_changed_at: Optional[datetime] = None
    status_changed_by: Optional[str] = None

# Common response models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    timestamp: str = CURRENT_TIMESTAMP
    user: str = CURRENT_USER

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    data: List[Any]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

# Common filter models
class BaseDateRangeFilter(BaseModel):
    """Base date range filter"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.strptime(CURRENT_TIMESTAMP, "%Y-%m-%d %H:%M:%S")
    )

class BaseUserFilter(BaseModel):
    """Base user filter"""
    user_id: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class BasePaginationParams(BaseModel):
    """Base pagination parameters"""
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_desc: bool = False

# Export all models
__all__ = [
    # Auth models
    "LoginRequest", "LoginResponse", "TokenResponse", "AdminLoginRequest",
    "RefreshTokenRequest", "PasswordResetRequest", "TwoFactorSetupResponse",
    "TwoFactorVerifyRequest",
    
    # User models
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserRole", "UserStatus",
    
    # Product models
    "ProductCreate", "ProductUpdate", "ProductResponse", "ProductFilter",
    
    # Stock models
    "StockResponse", "StockItem", "StockAddRequest", "StockReduceRequest",
    "StockHistoryResponse", "StockFilter",
    
    # Transaction models
    "TransactionResponse", "TransactionCreate", "TransactionFilter",
    "TransactionType", "TransactionStatus",
    
    # Balance models
    "BalanceResponse", "BalanceUpdateRequest", "BalanceHistoryResponse",
    "BalanceFilter", "BalanceType",
    
    # Dashboard models
    "SystemInfo", "UserActivity", "SystemStatus", "UserStats",
    "StockAlert", "DashboardStats", "UserDashboard", "DashboardSettings",
    
    # Admin models
    "AdminStats", "AdminDashboard",
    
    # Base models
    "BaseTimestampModel", "BaseStatusModel", "BaseResponse",
    "ErrorResponse", "PaginatedResponse",
    
    # Filter models
    "BaseDateRangeFilter", "BaseUserFilter", "BasePaginationParams",
    
    # Constants
    "CURRENT_TIMESTAMP", "CURRENT_USER"
]

# Version info
VERSION = "1.0.0"
API_VERSION = "v1"