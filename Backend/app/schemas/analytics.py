from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class DateRangePreset(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_YEAR = "this_year"
    CUSTOM = "custom"


class TimePeriod(BaseModel):
    start_date: datetime
    end_date: datetime
    preset: Optional[str] = None


class KPICard(BaseModel):
    value: Union[int, float]
    previous_value: Union[int, float] = 0
    change_percentage: float = 0.0


class DashboardKPIs(BaseModel):
    certificates_issued: KPICard
    active_certificates: KPICard
    revoked_certificates: KPICard
    emails_sent: KPICard
    emails_delivered: KPICard
    delivery_rate: KPICard
    verifications_successful: KPICard
    failed_operations: KPICard


class ChartDataset(BaseModel):
    name: str
    values: List[Union[int, float]]


class ChartData(BaseModel):
    labels: List[str] = []
    datasets: List[ChartDataset] = []


class StatusDistribution(BaseModel):
    active: int = 0
    revoked: int = 0
    expired: int = 0


class RecentJobSummary(BaseModel):
    id: str
    type: str  # "issuance" or "email"
    status: str
    total: int = 0
    processed: int = 0
    created_at: datetime


class DashboardOverviewResponse(BaseModel):
    period: TimePeriod
    kpis: DashboardKPIs
    issuance_trend: ChartData
    status_distribution: StatusDistribution
    recent_jobs: List[RecentJobSummary] = []
    recent_activities: List[Dict[str, Any]] = []


class CertificateAnalyticsResponse(BaseModel):
    period: TimePeriod
    total_issued: int
    active_count: int
    revoked_count: int
    expired_count: int
    issuance_trend: ChartData
    by_template: List[Dict[str, Any]] = []
    by_program: List[Dict[str, Any]] = []


class IssuanceAnalyticsResponse(BaseModel):
    period: TimePeriod
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    cancelled_jobs: int
    total_certificates_generated: int
    throughput_certs_per_minute: float
    average_duration_seconds: float
    error_breakdown: List[Dict[str, Any]] = []


class EmailAnalyticsResponse(BaseModel):
    period: TimePeriod
    queued: int
    sent: int
    delivered: int
    failed: int
    bounced: int
    complained: int
    delivery_rate: float
    bounce_rate: float
    failure_breakdown: List[Dict[str, Any]] = []


class VerificationAnalyticsResponse(BaseModel):
    period: TimePeriod
    total_attempts: int
    successful_valid: int
    revoked: int
    expired: int
    not_found_or_invalid: int
    verification_rate: float
    daily_trend: ChartData
    top_verified_certificates: List[Dict[str, Any]] = []


class TemplateAnalyticsResponse(BaseModel):
    total_templates: int
    items: List[Dict[str, Any]] = []


class ImportAnalyticsResponse(BaseModel):
    total_imports: int
    total_rows_processed: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    mapping_quality: Dict[str, Any] = {}


class UsageAnalyticsResponse(BaseModel):
    month: str
    certificates_issued: int
    certificates_limit: int = 10000
    emails_sent: int
    emails_limit: int = 10000
    verification_requests: int
    storage_used_bytes: int
    storage_used_mb: float
    storage_limit_mb: float = 10240.0
    storage_breakdown: Dict[str, float] = {}


class UnifiedTimelineEvent(BaseModel):
    type: str
    title: str
    description: str
    timestamp: datetime
    actor: Optional[str] = None
    metadata: Dict[str, Any] = {}


class UnifiedCertificateTimelineResponse(BaseModel):
    certificate_id: str
    certificate_number: str
    current_status: str
    events: List[UnifiedTimelineEvent] = []


class CertificateSearchQuery(BaseModel):
    query: Optional[str] = None
    status: Optional[str] = None
    template_id: Optional[str] = None
    program: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    page: int = 1
    limit: int = 20
