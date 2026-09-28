from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    permissions: List[str] = Field(..., min_items=1)


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    permissions: Optional[List[str]] = None


class RoleResponse(BaseModel):
    id: str
    organization_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    permissions: List[str]
    is_system_role: bool = False
    member_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoleListResponse(BaseModel):
    items: List[RoleResponse]
    total: int
