from __future__ import annotations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PlanEntitlements(BaseModel):
    max_certificates_monthly: int = Field(100, description="Monthly certificate quota (-1 for unlimited)")
    max_storage_bytes: int = Field(1073741824, description="Storage quota in bytes (default 1GB)")
    max_templates: int = Field(3, description="Maximum published templates allowed")
    max_members: int = Field(2, description="Maximum organization seats")
    max_teams: int = Field(1, description="Maximum teams allowed")
    max_webhooks: int = Field(0, description="Maximum outbound webhooks allowed")
    api_access: bool = Field(False, description="Developer REST API and API key access")
    custom_roles: bool = Field(False, description="Granular custom role creation")
    analytics_history_days: int = Field(30, description="Days of analytics history retained")
    csv_max_rows: int = Field(500, description="Maximum rows per bulk import batch")
    priority_worker_queue: bool = Field(False, description="Access to priority worker execution")
    white_label_email: bool = Field(False, description="Custom SMTP and branding in certificate emails")


class PlanResponse(BaseModel):
    plan_id: str
    name: str
    description: str
    price_monthly: int = Field(0, description="Monthly price in local currency units (e.g. INR)")
    price_yearly: int = Field(0, description="Annual price with discount in local currency units")
    currency: str = "INR"
    entitlements: PlanEntitlements
    features: List[str] = Field(default_factory=list)
    is_active: bool = True
    provider_price_id_monthly: Optional[str] = None
    provider_price_id_yearly: Optional[str] = None


class PlanListResponse(BaseModel):
    items: List[PlanResponse]
    total: int
