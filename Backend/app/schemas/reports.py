from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    CERTIFICATE_REPORT = "certificate_report"
    EMAIL_REPORT = "email_report"
    VERIFICATION_REPORT = "verification_report"
    ACTIVITY_REPORT = "activity_report"
    SUMMARY_REPORT = "summary_report"


class ReportFormat(str, Enum):
    CSV = "csv"
    PDF = "pdf"


class ReportStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ReportJobCreateRequest(BaseModel):
    type: ReportType = ReportType.CERTIFICATE_REPORT
    format: ReportFormat = ReportFormat.CSV
    date_range: Optional[str] = "last_30_days"
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    filters: Dict[str, Any] = Field(default_factory=dict)


class ReportJobResponse(BaseModel):
    id: str
    organization_id: str
    type: str
    format: str
    status: str
    filters: Dict[str, Any] = {}
    row_count: int = 0
    file_size_bytes: int = 0
    download_url: Optional[str] = None
    error: Optional[str] = None
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class ReportJobListResponse(BaseModel):
    items: List[ReportJobResponse]
    total: int
    page: int
    limit: int
    total_pages: int
