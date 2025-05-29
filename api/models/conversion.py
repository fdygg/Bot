from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class CurrencyType(str, Enum):
    WL = "wl"         # World Lock
    DL = "dl"         # Diamond Lock
    BGL = "bgl"       # Blue Gem Lock
    IDR = "idr"       # Indonesian Rupiah

class RateType(str, Enum):
    BUY = "buy"       # Buying rate (user sells to bot)
    SELL = "sell"     # Selling rate (user buys from bot)
    MIDDLE = "middle" # Middle rate (for calculations)

class ConversionRate(BaseModel):
    id: Optional[str] = None
    from_currency: CurrencyType
    to_currency: CurrencyType
    rate_type: RateType
    rate: float = Field(..., gt=0)
    effective_from: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-05-29 07:46:10",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    effective_until: Optional[datetime] = None
    created_by: str = Field(default="fdygg")
    created_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-05-29 07:46:10",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    updated_at: Optional[datetime] = None
    metadata: Dict = Field(default_factory=dict)

    @validator('to_currency')
    def validate_currency_pair(cls, v, values):
        if 'from_currency' in values:
            if v == values['from_currency']:
                raise ValueError("From and to currency must be different")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rate_123456",
                "from_currency": "wl",
                "to_currency": "idr",
                "rate_type": "sell",
                "rate": 1100.0,
                "effective_from": "2025-05-29 07:46:10",
                "created_by": "fdygg",
                "created_at": "2025-05-29 07:46:10",
                "metadata": {
                    "source": "manual",
                    "market_condition": "stable"
                }
            }
        }

class ConversionRequest(BaseModel):
    from_currency: CurrencyType
    to_currency: CurrencyType
    amount: float = Field(..., gt=0)
    rate_type: RateType = Field(default=RateType.MIDDLE)

    class Config:
        json_schema_extra = {
            "example": {
                "from_currency": "wl",
                "to_currency": "idr",
                "amount": 100,
                "rate_type": "sell"
            }
        }

class ConversionResponse(BaseModel):
    request: ConversionRequest
    result: float
    rate_used: float
    timestamp: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-05-29 07:46:10",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "request": {
                    "from_currency": "wl",
                    "to_currency": "idr",
                    "amount": 100,
                    "rate_type": "sell"
                },
                "result": 110000.0,
                "rate_used": 1100.0,
                "timestamp": "2025-05-29 07:46:10"
            }
        }

class RateUpdateRequest(BaseModel):
    currency_pairs: List[Dict[str, CurrencyType]] = Field(
        ...,
        description="List of currency pairs to update"
    )
    rates: Dict[RateType, float] = Field(
        ...,
        description="New rates for each rate type"
    )
    effective_from: Optional[datetime] = Field(
        default_factory=lambda: datetime.strptime(
            "2025-05-29 07:46:10",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    reason: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "currency_pairs": [
                    {
                        "from_currency": "wl",
                        "to_currency": "idr"
                    }
                ],
                "rates": {
                    "buy": 1000.0,
                    "sell": 1100.0,
                    "middle": 1050.0
                },
                "effective_from": "2025-05-29 07:46:10",
                "reason": "Market price adjustment",
                "metadata": {
                    "source": "manual",
                    "market_condition": "stable"
                }
            }
        }

class RateHistory(BaseModel):
    rates: List[ConversionRate]
    total: int
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "rates": [
                    {
                        "id": "rate_123456",
                        "from_currency": "wl",
                        "to_currency": "idr",
                        "rate_type": "sell",
                        "rate": 1100.0,
                        "effective_from": "2025-05-29 07:46:10",
                        "created_by": "fdygg",
                        "created_at": "2025-05-29 07:46:10",
                        "metadata": {
                            "source": "manual",
                            "market_condition": "stable"
                        }
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
        }

class RateAlert(BaseModel):
    id: Optional[str] = None
    currency_pair: Dict[str, CurrencyType]
    condition: str = Field(..., description="Price condition to trigger alert")
    threshold: float = Field(..., gt=0)
    status: str = Field(default="active")
    created_by: str = Field(default="fdygg")
    created_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-05-29 07:46:10",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    last_triggered: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert_123456",
                "currency_pair": {
                    "from_currency": "wl",
                    "to_currency": "idr"
                },
                "condition": "above",
                "threshold": 1200.0,
                "status": "active",
                "created_by": "fdygg",
                "created_at": "2025-05-29 07:46:10"
            }
        }