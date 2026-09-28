from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    scopes: List[str] = Field(..., min_items=1)
    service_account_id: Optional[str] = None
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    prefix: str
    scopes: List[str]
    status: str
    service_account_id: Optional[str] = None
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    # Plaintext key is returned only upon initial creation
    key: Optional[str] = None


class APIKeyListResponse(BaseModel):
    items: List[APIKeyResponse]
    total: int
