from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class UsageMetric(str, Enum):
    CERTIFICATES_GENERATED = "certificates_generated"
    EMAILS_SENT = "emails_sent"
    STORAGE_BYTES = "storage_bytes"
    API_REQUESTS = "api_requests"
    IMPORTS_PROCESSED = "imports_processed"
    VERIFICATION_REQUESTS = "verification_requests"
    WEBHOOK_DELIVERIES = "webhook_deliveries"
    REPORTS_GENERATED = "reports_generated"


class UsageItemResponse(BaseModel):
    used: int
    limit: int = Field(-1, description="-1 indicates unlimited quota")
    remaining: int = Field(-1, description="-1 indicates unlimited quota")
    usage_percentage: float = 0.0
    percent_used: float = 0.0
    warning_level: Optional[str] = Field(None, description="None, 'warning' (>=80%), 'critical' (>=90%), 'exceeded' (>=100%)")

    def __init__(self, **data: Any):
        if "usage_percentage" in data and "percent_used" not in data:
            data["percent_used"] = data["usage_percentage"]
        elif "percent_used" in data and "usage_percentage" not in data:
            data["usage_percentage"] = data["percent_used"]
        super().__init__(**data)


class UsageSummaryResponse(BaseModel):
    organization_id: str
    period: str = Field(..., description="Current billing period string YYYY-MM")
    plan_id: str
    metrics: Dict[str, UsageItemResponse]
    is_over_limit: bool = False
    warning_messages: list[str] = Field(default_factory=list)
