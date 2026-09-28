from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class IssuerProfileCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Legal or display name of the issuing authority")
    description: Optional[str] = Field(None, max_length=1000, description="Public description of the issuer")
    logo: Optional[str] = Field(None, description="Public logo URL or base64 data URI")
    website: Optional[str] = Field(None, description="Official website URL")
    email: Optional[str] = Field(None, description="Public support / contact email")
    phone: Optional[str] = Field(None, description="Public telephone")
    address: Optional[str] = Field(None, description="Physical headquarters address")


class IssuerProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    logo: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class IssuerProfileResponse(BaseModel):
    id: str
    organization_id: str
    issuer_id: str
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    issuer_url: str
    verification_url: str
    status: str = "active"
    active_key_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PublicIssuerKeyInfo(BaseModel):
    key_id: str
    algorithm: str
    public_key_pem: str
    status: str
    activated_at: datetime


class PublicIssuerProfileResponse(BaseModel):
    issuer_id: str
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    issuer_url: str
    verification_url: str
    public_keys: List[PublicIssuerKeyInfo] = Field(default_factory=list)
