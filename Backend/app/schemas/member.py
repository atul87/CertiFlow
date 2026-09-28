from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class MemberUserSummary(BaseModel):
    id: str
    name: str
    email: str


class MemberResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    role: str
    status: str
    joined_at: Optional[datetime] = None
    created_at: datetime
    user: Optional[MemberUserSummary] = None


class MemberListResponse(BaseModel):
    items: List[MemberResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class MemberInviteRequest(BaseModel):
    email: EmailStr
    role: str = "member"
    expires_in_days: Optional[int] = 7


class MemberInviteResponse(BaseModel):
    id: str
    organization_id: str
    email: str
    role: str
    status: str
    invited_by: str
    expires_at: datetime
    created_at: datetime
    invitation_token: Optional[str] = None  # Returned only upon invitation creation
    invitation_url: Optional[str] = None


class MemberInviteListResponse(BaseModel):
    items: List[MemberInviteResponse]
    total: int


class MemberAcceptInviteRequest(BaseModel):
    token: str
    name: Optional[str] = None
    password: Optional[str] = None


class MemberUpdateRequest(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None  # active, suspended


class OwnershipTransferRequest(BaseModel):
    new_owner_user_id: str
