from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class DeliveryStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    CANCELLED = "cancelled"


class DeliveryMode(str, Enum):
    LINK = "link"
    ATTACHMENT = "attachment"
    BOTH = "both"


class EmailJobStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    STARTING = "starting"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"
    CANCELLED = "cancelled"


# --- Email Templates ---

class EmailTemplateCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    html_body: str = Field(..., min_length=1)
    text_body: Optional[str] = None


class EmailTemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    status: Optional[str] = None


class EmailTemplateResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    subject: str
    html_body: str
    text_body: str
    variables: List[str] = []
    status: str = "active"
    created_by: str
    created_at: datetime
    updated_at: datetime


class EmailTemplateListResponse(BaseModel):
    items: List[EmailTemplateResponse]
    total: int


# --- Email Settings ---

class EmailSettingsUpdateRequest(BaseModel):
    provider: Optional[str] = None
    sender_name: Optional[str] = None
    sender_email: Optional[EmailStr] = None
    reply_to: Optional[EmailStr] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    api_key: Optional[str] = None
    auto_email_on_issuance: Optional[bool] = None


class EmailSettingsResponse(BaseModel):
    organization_id: str
    provider: str
    sender_name: str
    sender_email: str
    reply_to: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    has_smtp_password: bool = False
    has_api_key: bool = False
    auto_email_on_issuance: bool = False
    updated_at: Optional[datetime] = None


# --- Deliveries ---

class SendCertificateEmailRequest(BaseModel):
    template_id: Optional[str] = None
    delivery_mode: DeliveryMode = DeliveryMode.LINK
    recipient_email: Optional[EmailStr] = None


class EmailDeliveryResponse(BaseModel):
    id: str
    organization_id: str
    certificate_id: str
    issuance_job_id: Optional[str] = None
    email_job_id: Optional[str] = None
    recipient_email: str
    recipient_name: str
    template_id: Optional[str] = None
    provider: str
    delivery_mode: str
    status: str
    attempts: int = 0
    provider_message_id: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    queued_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    created_at: datetime


class EmailDeliveryListResponse(BaseModel):
    items: List[EmailDeliveryResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# --- Email Jobs ---

class EmailJobCreateRequest(BaseModel):
    certificate_ids: List[str] = Field(..., min_length=1)
    template_id: Optional[str] = None
    delivery_mode: DeliveryMode = DeliveryMode.LINK


class EmailJobResponse(BaseModel):
    id: str
    organization_id: str
    status: str
    total: int = 0
    queued: int = 0
    sending: int = 0
    sent: int = 0
    delivered: int = 0
    failed: int = 0
    bounced: int = 0
    progress: float = 0.0
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class EmailJobListResponse(BaseModel):
    items: List[EmailJobResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# --- Preview & Test ---

class EmailPreviewRequest(BaseModel):
    template_id: Optional[str] = None
    certificate_id: Optional[str] = None
    html_body: Optional[str] = None
    subject: Optional[str] = None


class EmailPreviewResponse(BaseModel):
    subject: str
    html: str
    text: str


class EmailTestRequest(BaseModel):
    template_id: Optional[str] = None
    recipient_email: EmailStr


# --- Suppressions ---

class EmailSuppressionResponse(BaseModel):
    id: str
    organization_id: str
    email: str
    reason: str
    created_at: datetime
