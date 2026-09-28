from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    VALID = "valid"
    REVOKED = "revoked"
    EXPIRED = "expired"
    NOT_FOUND = "not_found"
    INVALID = "invalid"


class PublicCertificateDetail(BaseModel):
    certificate_number: str
    recipient_name: str
    program_name: Optional[str] = None
    issue_date: Optional[str] = None
    issuer_name: Optional[str] = None
    issuer_website: Optional[str] = None
    issuer_logo_url: Optional[str] = None
    public_download_available: bool = True


class PublicVerificationResponse(BaseModel):
    valid: bool
    status: str
    certificate: Optional[PublicCertificateDetail] = None
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    verified_at: datetime
    message: Optional[str] = None


class FileVerificationResponse(BaseModel):
    valid: bool
    status: str
    integrity_matched: bool
    algorithm: str = "SHA-256"
    file_sha256: str
    certificate: Optional[PublicCertificateDetail] = None
    message: Optional[str] = None


class RevokeCertificateRequest(BaseModel):
    reason: str = Field(..., min_length=3, description="Reason for revocation")
    notes: Optional[str] = Field(None, description="Optional internal administrative notes")


class BulkRevokeRequest(BaseModel):
    certificate_ids: List[str] = Field(..., min_length=1, description="List of certificate IDs to revoke")
    reason: str = Field(..., min_length=3, description="Reason for bulk revocation")
    notes: Optional[str] = None


class BulkRevokeResponse(BaseModel):
    revoked_count: int
    failed_ids: List[str] = []
    message: str


class IntegrityCheckResponse(BaseModel):
    certificate_id: str
    certificate_number: str
    valid: bool
    algorithm: str = "SHA-256"
    stored_hash: Optional[str] = None
    current_hash: Optional[str] = None
    matched: bool
    checked_at: datetime


class VerificationEventResponse(BaseModel):
    id: str
    certificate_id: Optional[str] = None
    verification_code: str
    result: str
    timestamp: datetime
    user_agent: Optional[str] = None


class CertificateTimelineItem(BaseModel):
    type: str
    title: str
    timestamp: datetime
    actor: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CertificateTimelineResponse(BaseModel):
    certificate_id: str
    certificate_number: str
    events: List[CertificateTimelineItem]
