from __future__ import annotations
from typing import Dict, Any, Optional
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.entitlement_override_repository import EntitlementOverrideRepository


class EntitlementService:
    @classmethod
    async def get_org_plan(cls, org_id: str) -> Dict[str, Any]:
        """Fetch active plan document for the organization."""
        sub = await SubscriptionRepository.get_by_org_id(org_id)
        plan_id = sub.get("plan_id", "free") if sub else "free"
        plan = await PlanRepository.get_by_id(plan_id)
        return plan or await PlanRepository.get_by_id("free")

    @classmethod
    async def can_access_feature(cls, org_id: str, feature: str) -> bool:
        """
        Check boolean entitlement (e.g. 'api_access', 'custom_roles', 'priority_worker_queue').
        """
        # 1. Check overrides first
        overrides = await EntitlementOverrideRepository.get_active_overrides(org_id)
        if feature in overrides and overrides[feature] > 0:
            return True

        # 2. Check base plan
        plan = await cls.get_org_plan(org_id)
        entitlements = plan.get("entitlements", {})
        return bool(entitlements.get(feature, False))

    @classmethod
    async def get_limit(cls, org_id: str, metric: str) -> int:
        """
        Get integer limit for a metric (e.g. 'max_certificates_monthly', 'max_templates', 'max_members').
        Takes into account any administrative or promotional overrides.
        """
        plan = await cls.get_org_plan(org_id)
        entitlements = plan.get("entitlements", {})
        base_limit = int(entitlements.get(metric, 100))

        # Check for overrides
        overrides = await EntitlementOverrideRepository.get_active_overrides(org_id)
        override_qty = overrides.get(metric, 0)
        return base_limit + override_qty
