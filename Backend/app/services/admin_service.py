from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from collections import defaultdict

from app.core.database import DatabaseManager
from app.core.exceptions import NotFoundError
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.entitlement_override_repository import EntitlementOverrideRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.admin import AdminPlatformOverviewResponse


class AdminService:
    @classmethod
    async def get_platform_overview(cls) -> AdminPlatformOverviewResponse:
        """Aggregate global SaaS KPIs, MRR, subscriptions, and platform usage."""
        db = DatabaseManager.get_db()

        total_orgs = await db["organizations"].count_documents({"status": {"$ne": "archived"}})

        # Subscriptions breakdown
        subs = await SubscriptionRepository.list_all(skip=0, limit=10000)
        active_cnt = 0
        trial_cnt = 0
        past_due_cnt = 0
        cancelled_cnt = 0
        mrr = 0
        plan_counts = defaultdict(int)

        plans_map = {p["plan_id"]: p for p in await PlanRepository.list_active_plans()}

        for s in subs:
            st = s.get("status", "active")
            pid = s.get("plan_id", "free")
            plan_counts[pid] += 1

            if st == "active":
                active_cnt += 1
                plan = plans_map.get(pid, {})
                mrr += plan.get("price_monthly", 0)
            elif st == "trialing":
                trial_cnt += 1
            elif st == "past_due":
                past_due_cnt += 1
            elif st == "cancelled":
                cancelled_cnt += 1

        total_certs = await db["certificates"].count_documents({})
        total_emails = await db["email_deliveries"].count_documents({})
        total_usage_events = await db["usage_events"].count_documents({})

        return AdminPlatformOverviewResponse(
            total_organizations=total_orgs,
            active_subscriptions=active_cnt,
            trial_subscriptions=trial_cnt,
            past_due_subscriptions=past_due_cnt,
            cancelled_subscriptions=cancelled_cnt,
            monthly_recurring_revenue=mrr,
            total_certificates_issued=total_certs,
            total_emails_sent=total_emails,
            total_usage_events=total_usage_events,
            subscriptions_by_plan=dict(plan_counts)
        )

    @classmethod
    async def override_subscription(
        cls,
        org_id: str,
        plan_id: str,
        status: Optional[str] = "active",
        reason: Optional[str] = None,
        admin_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manually override an organization's subscription plan and status."""
        plan = await PlanRepository.get_by_id(plan_id)
        if not plan:
            raise NotFoundError(message=f"Plan '{plan_id}' does not exist", code="PLAN_NOT_FOUND")

        sub = await SubscriptionRepository.upsert_subscription(
            organization_id=org_id,
            plan_id=plan_id,
            status=status or "active",
            provider="admin_override"
        )

        await AuditLogRepository.log_event(
            action="admin.subscription.modified",
            resource_type="subscription",
            resource_id=sub.get("id"),
            organization_id=org_id,
            user_id=admin_user_id,
            metadata={"plan_id": plan_id, "status": status, "reason": reason}
        )
        return sub

    @classmethod
    async def grant_entitlement_override(
        cls,
        org_id: str,
        feature: str,
        quantity: int,
        reason: str,
        expires_in_days: int = 30,
        admin_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Grant a promotional or support quota override."""
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days) if expires_in_days else None
        res = await EntitlementOverrideRepository.grant_override(
            organization_id=org_id,
            feature=feature,
            quantity=quantity,
            reason=reason,
            created_by=admin_user_id,
            expires_at=expires_at
        )

        await AuditLogRepository.log_event(
            action="admin.entitlement.granted",
            resource_type="entitlement",
            resource_id=feature,
            organization_id=org_id,
            user_id=admin_user_id,
            metadata={"feature": feature, "quantity": quantity, "reason": reason, "expires_at": str(expires_at)}
        )
        return res

    @classmethod
    async def suspend_organization(
        cls,
        org_id: str,
        reason: str,
        admin_user_id: Optional[str] = None
    ) -> bool:
        """Suspend organization for abuse or non-payment."""
        from bson import ObjectId
        query = {"$or": [{"_id": ObjectId(org_id) if ObjectId.is_valid(org_id) else org_id}, {"id": org_id}]}
        await DatabaseManager.get_collection("organizations").update_one(
            query,
            {"$set": {"status": "suspended", "is_active": False, "suspension_reason": reason}}
        )
        await SubscriptionRepository.update_status(org_id, "paused")

        await AuditLogRepository.log_event(
            action="admin.organization.suspended",
            resource_type="organization",
            resource_id=org_id,
            organization_id=org_id,
            user_id=admin_user_id,
            metadata={"reason": reason}
        )
        return True

    @classmethod
    async def restore_organization(
        cls,
        org_id: str,
        admin_user_id: Optional[str] = None
    ) -> bool:
        """Restore suspended organization."""
        from bson import ObjectId
        query = {"$or": [{"_id": ObjectId(org_id) if ObjectId.is_valid(org_id) else org_id}, {"id": org_id}]}
        await DatabaseManager.get_collection("organizations").update_one(
            query,
            {"$set": {"status": "active", "is_active": True, "suspension_reason": None}}
        )
        await SubscriptionRepository.update_status(org_id, "active")

        await AuditLogRepository.log_event(
            action="admin.organization.restored",
            resource_type="organization",
            resource_id=org_id,
            organization_id=org_id,
            user_id=admin_user_id
        )
        return True
