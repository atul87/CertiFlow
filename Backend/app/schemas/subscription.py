from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.plan import PlanResponse


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubscriptionResponse(BaseModel):
    id: str
    organization_id: str
    plan_id: str
    status: str
    billing_interval: str = "monthly"
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    trial_ends_at: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    plan: Optional[PlanResponse] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> SubscriptionResponse:
        d = dict(data)
        if "trial_ends_at" in d and "trial_end" not in d:
            d["trial_end"] = d["trial_ends_at"]
        elif "trial_end" in d and "trial_ends_at" not in d:
            d["trial_ends_at"] = d["trial_end"]
        return cls(**d)


class CheckoutRequest(BaseModel):
    plan_id: str = Field(..., description="Target plan ID ('starter', 'pro', 'business', 'enterprise')")
    billing_interval: str = Field("monthly", description="'monthly' or 'yearly'")
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    provider: str
    plan_id: str


class SubscriptionCancelRequest(BaseModel):
    immediate: bool = Field(False, description="If True, cancel immediately without waiting for period end")
    reason: Optional[str] = Field(None, description="Reason for cancellation feedback")


class SubscriptionResumeResponse(BaseModel):
    message: str
    status: str
    cancel_at_period_end: bool
