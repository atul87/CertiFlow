from __future__ import annotations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, model_validator


class AdminPlatformOverviewResponse(BaseModel):
    total_organizations: int
    active_subscriptions: int
    trial_subscriptions: int
    past_due_subscriptions: int
    cancelled_subscriptions: int
    monthly_recurring_revenue: int
    mrr: int = 0
    total_certificates_issued: int
    total_emails_sent: int
    total_usage_events: int
    subscriptions_by_plan: Dict[str, int]
    subscriptions_by_status: Dict[str, int] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "mrr" not in data or not data["mrr"]:
                data["mrr"] = data.get("monthly_recurring_revenue", 0)
            if "subscriptions_by_status" not in data or not data["subscriptions_by_status"]:
                data["subscriptions_by_status"] = {
                    "active": data.get("active_subscriptions", 0),
                    "trialing": data.get("trial_subscriptions", 0),
                    "past_due": data.get("past_due_subscriptions", 0),
                    "cancelled": data.get("cancelled_subscriptions", 0),
                }
        return data


class AdminEntitlementGrantRequest(BaseModel):
    feature: Optional[str] = None
    metric: Optional[str] = None
    quantity: Optional[int] = None
    additional_quantity: Optional[int] = None
    reason: Optional[str] = "Administrative override"
    duration_days: Optional[int] = None
    expires_in_days: Optional[int] = 30

    @model_validator(mode="after")
    def normalize_fields(self):
        if not self.feature and self.metric:
            self.feature = self.metric
        if self.quantity is None and self.additional_quantity is not None:
            self.quantity = self.additional_quantity
        if self.duration_days is None and self.expires_in_days is not None:
            self.duration_days = self.expires_in_days
        return self


class AdminSubscriptionOverrideRequest(BaseModel):
    plan_id: str = Field(..., description="Target plan ID ('free', 'starter', 'pro', 'business', 'enterprise')")
    status: Optional[str] = Field("active", description="Optional override status ('active', 'trialing', 'past_due')")
    reason: Optional[str] = Field("Support action", description="Support reason or contract reference")
