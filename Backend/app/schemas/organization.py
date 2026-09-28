from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    owner_id: str
    plan: str = "free"
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Organization name cannot be empty")
            return cleaned
        return v


class MemberUserSummary(BaseModel):
    id: str
    name: str
    email: str


class OrganizationMemberResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    role: str  # owner, admin, member
    status: str  # active, suspended
    created_at: datetime
    user: Optional[MemberUserSummary] = None

    class Config:
        from_attributes = True
