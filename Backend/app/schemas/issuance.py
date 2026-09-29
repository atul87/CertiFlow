from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    QUEUED = "queued"
    STARTING = "starting"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    PARTIALLY_FAILED = "partially_failed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ItemStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ZipStatus(str, Enum):
    NOT_REQUESTED = "not_requested"
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"


class IssuanceJobCreateRequest(BaseModel):
    import_id: str = Field(..., description="ID of the validated import")
    template_version_id: str = Field(..., description="ID of the published template version")


class IssuanceJobResponse(BaseModel):
    id: str
    organization_id: str
    template_id: str
    template_version_id: str
    import_id: str
    status: str
    total: int = 0
    pending: int = 0
    processing: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    progress: float = 0.0
    created_by: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    zip_info: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class IssuanceJobProgressResponse(BaseModel):
    job_id: str
    status: str
    total: int
    completed: int
    processing: int
    failed: int
    pending: int
    cancelled: int = 0
    progress: float


class IssuanceItemResponse(BaseModel):
    id: str
    job_id: str
    organization_id: str
    import_row_id: str
    row_number: int
    status: str
    certificate_id: Optional[str] = None
    attempts: int = 0
    error: Optional[Dict[str, Any]] = None
    recipient: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class IssuanceItemListResponse(BaseModel):
    items: List[IssuanceItemResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class IssuanceJobListResponse(BaseModel):
    items: List[IssuanceJobResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class ZipStatusResponse(BaseModel):
    job_id: str
    status: str
    download_url: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None


class ErrorRowItem(BaseModel):
    row_number: int
    recipient_name: str
    email: str
    error_code: str
    error_message: str
    attempts: int
