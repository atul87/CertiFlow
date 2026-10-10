"""
Typed domain entities and document structures for database collections.
Provides compile-time typing, IDE autocomplete, and explicit schemas for internal persistence.
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class UserDoc(TypedDict, total=False):
    id: str
    email: str
    password_hash: str
    name: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime


class OrganizationDoc(TypedDict, total=False):
    id: str
    name: str
    slug: str
    owner_id: str
    plan_tier: str
    created_at: datetime
    updated_at: datetime


class CertificateDoc(TypedDict, total=False):
    id: str
    organization_id: str
    template_id: str
    certificate_number: str
    verification_code: str
    recipient_name: str
    recipient_email: str
    program_name: str
    issue_date: str
    expiry_date: Optional[str]
    status: str
    metadata: Dict[str, Any]
    revoked_at: Optional[datetime]
    revocation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime


class TemplateDoc(TypedDict, total=False):
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    status: str
    current_version_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class IssuanceJobDoc(TypedDict, total=False):
    id: str
    organization_id: str
    template_id: str
    total_recipients: int
    processed_count: int
    failed_count: int
    status: str
    created_at: datetime
    updated_at: datetime
