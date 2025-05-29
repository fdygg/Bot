from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class BlacklistType(str, Enum):
    USER = "user"
    IP = "ip"
    DEVICE = "device"
    PAYMENT = "payment"

class BlacklistReason(str, Enum):
    SPAM = "spam"
    FRAUD = "fraud"
    ABUSE = "abuse"
    SUSPICIOUS = "suspicious"
    MANUAL = "manual"

class BlacklistStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REMOVED = "removed"

class BlacklistEntry(BaseModel):
    id: Optional[str] = None
    type: BlacklistType
    value: str = Field(..., description="User ID, IP, or other identifier")
    reason: BlacklistReason
    description: Optional[str] = None
    evidence: List[Dict] = Field(default_factory=list)
    status: BlacklistStatus = Field(default=BlacklistStatus.ACTIVE)
    expires_at: Optional[datetime] = None
    created_by: str = Field(default="fdygg")
    created_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-05-29 07:48:17",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    metadata: Dict = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "bl_123456",
                "type": "user",
                "value": "usr_123456",
                "reason": "fraud",
                "description": "Multiple chargeback attempts",
                "evidence": [
                    {
                        "type": "transaction",
                        "id": "tx_123456",
                        "details": "Chargeback on WL purchase"
                    }
                ],
                "status": "active",
                "created_by": "fdygg",
                "created_at": "2025-05-29 07:48:17"
            }
        }

class FraudDetectionRule(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    conditions: Dict = Field(..., description="Rule conditions")
    actions: List[Dict] = Field(..., description="Actions to take when triggered")
    is_active: bool = Field(default=True)
    created_by: str = Field(default="fdygg")
    created_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-05-29 07:48:17",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rule_123456",
                "name": "Multiple Account Detection",
                "description": "Detect multiple accounts from same IP",
                "conditions": {
                    "type": "ip_address",
                    "threshold": 5,
                    "time_window": 3600
                },
                "actions": [
                    {
                        "type": "blacklist",
                        "target": "ip",
                        "duration": 86400
                    },
                    {
                        "type": "notify",
                        "channel": "discord",
                        "role": "moderator"
                    }
                ],
                "is_active": True,
                "created_by": "fdygg",
                "created_at": "2025-05-29 07:48:17"
            }
        }