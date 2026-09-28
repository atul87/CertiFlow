from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CertificatePreviewRequest(BaseModel):
    """Request body for POST /certificates/preview — P3.45"""
    template_version_id: str = Field(..., description="Published template version ID")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Recipient / field data for placeholder substitution"
    )


class CertificateGenerateRequest(BaseModel):
    """Request body for POST /certificates/generate — P3.47"""
    template_version_id: str = Field(..., description="Published template version ID")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Recipient / field data for placeholder substitution"
    )
    import_id: Optional[str] = Field(None, description="Optional import batch ID")
    import_row_id: Optional[str] = Field(None, description="Optional import row ID")


class CertificateFileInfo(BaseModel):
    pdf_key: Optional[str] = None
    preview_key: Optional[str] = None
    pdf_size: Optional[int] = None
    preview_size: Optional[int] = None
    sha256: Optional[str] = None


class CertificateResponse(BaseModel):
    """Serialized certificate document returned from API — P3.57"""
    id: str
    organization_id: str
    template_id: str
    template_version_id: str
    certificate_number: str
    verification_code: str
    recipient: Dict[str, Any]
    data: Dict[str, Any]
    template_snapshot: Dict[str, Any]
    status: str
    file: Optional[CertificateFileInfo] = None
    render_diagnostics: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    issued_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    revoked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CertificatePreviewResponse(BaseModel):
    """Response for preview render — P3.46"""
    preview_url: str = Field(..., description="Base64 PNG data URL")
    overflows: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="SmartFit overflow warnings"
    )
    render_time_ms: float = 0.0
    diagnostics: Optional[Dict[str, Any]] = None


class CertificateListResponse(BaseModel):
    items: List[CertificateResponse]
    page: int
    limit: int
    total: int
    total_pages: int


class CertificateRevokeRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500, description="Reason for revocation")


class CertificateVerifyResponse(BaseModel):
    """Public verification result — P3.65"""
    valid: bool
    certificate_number: Optional[str] = None
    recipient_name: Optional[str] = None
    template_name: Optional[str] = None
    issued_at: Optional[datetime] = None
    status: Optional[str] = None
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
