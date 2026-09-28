from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.member import MemberUserSummary


class TeamCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=250)


class TeamUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=250)


class TeamMemberAddRequest(BaseModel):
    user_id: str
    role: Optional[str] = "member"


class TeamMemberResponse(BaseModel):
    id: str
    team_id: str
    user_id: str
    organization_id: str
    role: str = "member"
    created_at: datetime
    user: Optional[MemberUserSummary] = None


class TeamResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    member_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None


class TeamListResponse(BaseModel):
    items: List[TeamResponse]
    total: int
