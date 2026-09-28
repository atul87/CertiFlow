from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class CredentialStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    ISSUED = "issued"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    REVOKED = "revoked"


class CredentialFormat(str, Enum):
    W3C_VC = "w3c_vc"
    OPEN_BADGES_V3 = "open_badges_v3"


class ProofDetails(BaseModel):
    type: str = "Ed25519Signature2020"
    created: datetime
    verification_method: str
    proof_purpose: str = "assertionMethod"
    proof_value: str


class CredentialEvidenceItem(BaseModel):
    name: str = Field(..., description="Evidence title or artifact label")
    type: str = Field("assessment", description="'project', 'assessment', 'repository', 'course', 'document'")
    description: Optional[str] = None
    url: Optional[str] = None
    is_public: bool = False


class CredentialCreateRequest(BaseModel):
    certificate_id: str = Field(..., description="ID of generated certificate to anchor credential to")
    achievement_id: Optional[str] = Field(None, description="Optional achievement ID (if omitted, created automatically from certificate template)")
    valid_from: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    evidence: Optional[List[CredentialEvidenceItem]] = None


class CredentialRevokeRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500, description="Audit reason for revocation")


class CredentialResponse(BaseModel):
    id: str
    credential_id: str
    organization_id: str
    certificate_id: str
    certificate_number: str
    verification_code: str
    issuer_id: str
    achievement_id: str
    status: str
    recipient_name: str
    recipient_email: str
    valid_from: datetime
    expires_at: Optional[datetime] = None
    credential_url: str
    verification_url: str
    badge_url: str
    vc_url: str
    signature_algorithm: str
    key_id: str
    proof: Optional[Dict[str, Any]] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class PublicCredentialResponse(BaseModel):
    """
    Privacy-safe public presentation.
    Opaque credential identifier without exposing personal emails, phone numbers, or internal DB IDs.
    """
    credential_id: str
    status: str
    recipient_name: str
    achievement_name: str
    achievement_description: str
    achievement_criteria: str
    achievement_skills: List[str] = Field(default_factory=list)
    issuer_name: str
    issuer_url: str
    issued_at: datetime
    expires_at: Optional[datetime] = None
    credential_url: str
    verification_url: str
    badge_url: str
    vc_url: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class CredentialVerificationResponse(BaseModel):
    valid: bool
    verification_status: str = Field(
        ...,
        description="'VALID', 'INVALID_SIGNATURE', 'REVOKED', 'EXPIRED', 'SUSPENDED', 'UNKNOWN_ISSUER', 'UNKNOWN_KEY', 'MALFORMED', 'NOT_FOUND'"
    )
    credential_id: Optional[str] = None
    recipient_name: Optional[str] = None
    achievement_name: Optional[str] = None
    issuer_name: Optional[str] = None
    issuer_id: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    signature_valid: bool = False
    status_valid: bool = False
    message: str


class ExternalVerificationRequest(BaseModel):
    """Payload for independent, standards-based verification of external or raw JSON credentials."""
    credential_payload: Dict[str, Any] = Field(..., description="Raw W3C Verifiable Credential or Open Badges v3 JSON")
