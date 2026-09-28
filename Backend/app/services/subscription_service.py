from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.billing_customer_repository import BillingCustomerRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.billing.provider_adapter import BillingProviderAdapter
from app.schemas.subscription import (
    SubscriptionResponse,
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionResumeResponse
)
from app.schemas.plan import PlanResponse


class SubscriptionService:
    @classmethod
    async def initialize_org_subscription(
        cls,
        org_id: str,
        plan_id: str = "free",
        trial: bool = True
    ) -> Dict[str, Any]:
        """
        Initialize default subscription when an organization is registered.
        If trial is True, grants 14-day trial on Starter tier.
        """
        now = datetime.now(timezone.utc)
        existing = await SubscriptionRepository.get_by_org_id(org_id)
        if existing:
            return existing

        target_plan = "starter" if trial else plan_id
        sub_status = "trialing" if trial else "active"
        trial_ends = now + timedelta(days=settings.DEFAULT_TRIAL_DAYS) if trial else None
        period_end = trial_ends if trial else (now + timedelta(days=30))

        sub = await SubscriptionRepository.upsert_subscription(
            organization_id=org_id,
            plan_id=target_plan,
            status=sub_status,
            billing_interval="monthly",
            current_period_start=now,
            current_period_end=period_end,
            trial_ends_at=trial_ends,
            provider="mock"
        )
        return sub

    @classmethod
    async def get_subscription(cls, org_id: str) -> SubscriptionResponse:
        """Fetch subscription details with joined plan information."""
        sub = await SubscriptionRepository.get_by_org_id(org_id)
        if not sub:
            # Auto-initialize if missing
            sub = await cls.initialize_org_subscription(org_id, plan_id="free", trial=False)

        plan_id = sub.get("plan_id", "free")
        plan_doc = await PlanRepository.get_by_id(plan_id)
        plan_resp = PlanResponse(**plan_doc) if plan_doc else None

        return SubscriptionResponse(
            id=sub["id"],
            organization_id=sub["organization_id"],
            plan_id=sub["plan_id"],
            status=sub.get("status", "active"),
            billing_interval=sub.get("billing_interval", "monthly"),
            current_period_start=sub.get("current_period_start", datetime.now(timezone.utc)),
            current_period_end=sub.get("current_period_end", datetime.now(timezone.utc)),
            cancel_at_period_end=sub.get("cancel_at_period_end", False),
            cancelled_at=sub.get("cancelled_at"),
            trial_ends_at=sub.get("trial_ends_at"),
            trial_end=sub.get("trial_ends_at"),
            plan=plan_resp,
            created_at=sub.get("created_at", datetime.now(timezone.utc)),
            updated_at=sub.get("updated_at", datetime.now(timezone.utc))
        )

    @classmethod
    async def create_checkout_session(
        cls,
        org_id: str,
        data: CheckoutRequest,
        user_email: str
    ) -> CheckoutResponse:
        """Create checkout session for plan upgrade or subscription purchase."""
        plan = await PlanRepository.get_by_id(data.plan_id)
        if not plan:
            raise NotFoundError(message=f"Plan '{data.plan_id}' does not exist", code="PLAN_NOT_FOUND")

        provider = BillingProviderAdapter.get_provider()

        # Ensure customer exists with provider
        cust = await BillingCustomerRepository.get_by_org_id(org_id)
        if not cust:
            prov_cust_id = await provider.create_customer(org_id=org_id, email=user_email)
            await BillingCustomerRepository.upsert_customer(
                organization_id=org_id,
                provider=provider.name,
                provider_customer_id=prov_cust_id,
                email=user_email
            )
        else:
            prov_cust_id = cust["provider_customer_id"]

        session_dict = await provider.create_checkout_session(
            customer_id=prov_cust_id,
            plan_id=data.plan_id,
            billing_interval=data.billing_interval,
            success_url=data.success_url,
            cancel_url=data.cancel_url,
            metadata={"organization_id": org_id, "plan_id": data.plan_id}
        )

        return CheckoutResponse(
            checkout_url=session_dict["checkout_url"],
            session_id=session_dict["session_id"],
            provider=provider.name,
            plan_id=data.plan_id
        )

    @classmethod
    async def cancel_subscription(
        cls,
        org_id: str,
        immediate: bool = False,
        reason: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SubscriptionResponse:
        """Cancel subscription immediately or schedule cancellation at period end."""
        sub = await SubscriptionRepository.get_by_org_id(org_id)
        if not sub:
            raise NotFoundError(message="No active subscription found", code="SUBSCRIPTION_NOT_FOUND")

        new_status = "cancelled" if immediate else sub.get("status", "active")
        updated = await SubscriptionRepository.update_status(
            organization_id=org_id,
            status=new_status,
            cancel_at_period_end=True
        )

        await AuditLogRepository.log_event(
            action="subscription.cancelled",
            resource_type="subscription",
            resource_id=sub["id"],
            organization_id=org_id,
            user_id=user_id,
            metadata={"immediate": immediate, "reason": reason}
        )
        return await cls.get_subscription(org_id)

    @classmethod
    async def resume_subscription(cls, org_id: str, user_id: Optional[str] = None) -> SubscriptionResumeResponse:
        """Resume a subscription scheduled for cancellation at period end."""
        sub = await SubscriptionRepository.get_by_org_id(org_id)
        if not sub or not sub.get("cancel_at_period_end"):
            raise ConflictError(message="Subscription is not pending cancellation", code="SUBSCRIPTION_NOT_CANCELLING")

        await SubscriptionRepository.update_status(
            organization_id=org_id,
            status="active",
            cancel_at_period_end=False
        )

        await AuditLogRepository.log_event(
            action="subscription.resumed",
            resource_type="subscription",
            resource_id=sub["id"],
            organization_id=org_id,
            user_id=user_id
        )
        return SubscriptionResumeResponse(
            message="Subscription has been successfully resumed.",
            status="active",
            cancel_at_period_end=False
        )
