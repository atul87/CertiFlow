from __future__ import annotations
from app.core.exceptions import ForbiddenError
from app.core.database import DatabaseManager
from app.repositories.usage_counter_repository import UsageCounterRepository
from app.services.entitlement_service import EntitlementService
from app.services.usage_service import UsageService


class QuotaService:
    @classmethod
    async def check_certificate_quota(cls, org_id: str, quantity: int = 1) -> bool:
        """
        Verify that issuing 'quantity' certificates will not exceed the organization's monthly quota.
        """
        limit = await EntitlementService.get_limit(org_id, "max_certificates_monthly")
        if limit < 0:
            return True  # Unlimited

        period = UsageService.current_period()
        current_used = await UsageCounterRepository.get_counter(org_id, "certificates_generated", period)
        if (current_used + quantity) > limit:
            raise ForbiddenError(
                message=f"Monthly certificate quota exceeded. Used: {current_used}, Requested: {quantity}, Plan Limit: {limit}. Please upgrade your plan.",
                code="CERTIFICATE_QUOTA_EXCEEDED"
            )
        return True

    @classmethod
    async def check_template_quota(cls, org_id: str) -> bool:
        """Verify that organization has not exceeded maximum templates allowed."""
        limit = await EntitlementService.get_limit(org_id, "max_templates")
        if limit < 0:
            return True

        templates_count = await DatabaseManager.get_collection("templates").count_documents({
            "organization_id": org_id,
            "status": {"$ne": "archived"}
        })
        if templates_count >= limit:
            raise ForbiddenError(
                message=f"Template limit of {limit} reached for your plan. Please upgrade your subscription to create additional templates.",
                code="TEMPLATE_QUOTA_EXCEEDED"
            )
        return True

    @classmethod
    async def check_member_quota(cls, org_id: str) -> bool:
        """Verify that organization has not exceeded maximum member seats."""
        limit = await EntitlementService.get_limit(org_id, "max_members")
        if limit < 0:
            return True

        members_count = await DatabaseManager.get_collection("organization_members").count_documents({
            "organization_id": org_id,
            "status": "active"
        })
        if members_count >= limit:
            raise ForbiddenError(
                message=f"Member limit of {limit} seats reached. Upgrade your plan to invite additional team members.",
                code="MEMBER_QUOTA_EXCEEDED"
            )
        return True

    @classmethod
    async def check_webhook_quota(cls, org_id: str) -> bool:
        """Verify that organization has not exceeded maximum webhook endpoints."""
        limit = await EntitlementService.get_limit(org_id, "max_webhooks")
        if limit < 0:
            return True

        webhook_count = await DatabaseManager.get_collection("webhook_endpoints").count_documents({
            "organization_id": org_id,
            "status": "active"
        })
        if webhook_count >= limit:
            raise ForbiddenError(
                message=f"Webhook endpoint limit of {limit} reached. Upgrade your subscription to register additional webhooks.",
                code="WEBHOOK_QUOTA_EXCEEDED"
            )
        return True

    @classmethod
    async def check_api_access(cls, org_id: str) -> bool:
        """Verify that organization's plan entitles developer API & API key usage."""
        has_access = await EntitlementService.can_access_feature(org_id, "api_access")
        if not has_access:
            raise ForbiddenError(
                message="Developer API and API Key access is not available on your current plan. Please upgrade to Starter or above.",
                code="API_ACCESS_NOT_ENTITLED"
            )
        return True
