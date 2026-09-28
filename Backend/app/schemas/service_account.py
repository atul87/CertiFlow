from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ServiceAccountCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=250)


class ServiceAccountUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=250)
    status: Optional[str] = None


class ServiceAccountResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    api_keys_count: int = 0


class ServiceAccountListResponse(BaseModel):
    items: List[ServiceAccountResponse]
    total: int
