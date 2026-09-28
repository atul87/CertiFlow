import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from app.repositories.plan_repository import PlanRepository, DEFAULT_PLANS
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.usage_counter_repository import UsageCounterRepository
from app.repositories.entitlement_override_repository import EntitlementOverrideRepository
from app.services.plan_service import PlanService
from app.services.entitlement_service import EntitlementService
from app.services.usage_service import UsageService
from app.services.quota_service import QuotaService
from app.services.cost_service import CostService
from app.core.exceptions import ForbiddenError


@pytest.mark.asyncio
async def test_plan_catalog_defaults():
    """Verify that default plans are present and contain valid entitlements."""
    plans = await PlanService.list_active_plans()
    assert len(plans) >= 5
    plan_ids = [p["plan_id"] for p in plans]
    assert "free" in plan_ids
    assert "starter" in plan_ids
    assert "pro" in plan_ids
    assert "business" in plan_ids
    assert "enterprise" in plan_ids

    free_plan = await PlanService.get_plan("free")
    assert free_plan.price_monthly == 0
    assert free_plan.entitlements.max_certificates_monthly == 100
    assert free_plan.entitlements.api_access is False

    pro_plan = await PlanService.get_plan("pro")
    assert pro_plan.price_monthly == 1999
    assert pro_plan.entitlements.max_certificates_monthly == 5000
    assert pro_plan.entitlements.api_access is True


@pytest.mark.asyncio
async def test_entitlement_service_and_promotional_overrides():
    """Verify entitlement checks respect base plan and support overrides."""
    org_id = "test_org_entitlements_123"

    # With no subscription, organization falls back to free
    limit = await EntitlementService.get_limit(org_id, "max_certificates_monthly")
    assert limit == 100
    has_api = await EntitlementService.can_access_feature(org_id, "api_access")
    assert has_api is False

    # Grant promotional override: +500 certificates and enable api_access
    await EntitlementOverrideRepository.grant_override(
        org_id=org_id,
        metric="max_certificates_monthly",
        quantity=500,
        reason="Promotional hackathon grant",
        granted_by="admin_test",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    await EntitlementOverrideRepository.grant_override(
        org_id=org_id,
        metric="api_access",
        quantity=1,
        reason="API evaluation grant",
        granted_by="admin_test",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    limit_after = await EntitlementService.get_limit(org_id, "max_certificates_monthly")
    assert limit_after == 600
    has_api_after = await EntitlementService.can_access_feature(org_id, "api_access")
    assert has_api_after is True


@pytest.mark.asyncio
async def test_usage_service_and_warning_thresholds():
    """Verify usage recording, period calculation, and warning calculation."""
    org_id = "test_org_usage_metering_456"
    period = UsageService.current_period()
    assert len(period) == 7  # YYYY-MM format

    # Record 85 certificates used out of 100 (free plan = 100 limit -> 85%)
    await UsageService.record_usage(
        org_id=org_id,
        metric="certificates_generated",
        quantity=85,
        resource_id="cert_bulk_1",
        source="test",
    )

    summary = await UsageService.get_usage_summary(org_id)
    assert summary.organization_id == org_id
    assert summary.period == period

    cert_metric = summary.metrics["certificates_generated"]
    assert cert_metric.used == 85
    assert cert_metric.limit == 100
    assert cert_metric.remaining == 15
    assert cert_metric.percent_used == 85.0
    assert cert_metric.warning_level == "warning"  # >= 80%

    # Add 10 more (95% -> strong_warning)
    await UsageService.record_usage(
        org_id=org_id,
        metric="certificates_generated",
        quantity=10,
        resource_id="cert_bulk_2",
        source="test",
    )
    summary2 = await UsageService.get_usage_summary(org_id)
    assert summary2.metrics["certificates_generated"].percent_used == 95.0
    assert summary2.metrics["certificates_generated"].warning_level in ("critical", "strong_warning")


@pytest.mark.asyncio
async def test_quota_service_hard_limits():
    """Verify QuotaService raises ForbiddenError when quota is exceeded."""
    org_id = "test_org_quota_hard_limit_789"
    period = UsageService.current_period()

    # Pre-fill counter to 99 out of 100 limit
    await UsageCounterRepository.increment_counter(org_id, "certificates_generated", period, 99)

    # 1 certificate should pass
    can_generate_one = await QuotaService.check_certificate_quota(org_id, quantity=1)
    assert can_generate_one is True

    # 2 certificates should fail with ForbiddenError
    with pytest.raises(ForbiddenError) as exc_info:
        await QuotaService.check_certificate_quota(org_id, quantity=2)
    assert exc_info.value.code == "CERTIFICATE_QUOTA_EXCEEDED"


@pytest.mark.asyncio
async def test_cost_service_calculations():
    """Verify internal cost estimation and unit economics calculation."""
    org_id = "test_org_cost_999"
    # Estimate costs for an org that generated 1,000 certificates
    await UsageService.record_usage(
        org_id=org_id,
        metric="certificates_generated",
        quantity=1000,
        source="test"
    )

    cost_data = await CostService.estimate_monthly_cost(org_id)
    assert cost_data["certificates_generated"] == 1000
    assert cost_data["total_estimated_cost_inr"] > 0
    assert cost_data["cost_per_certificate_inr"] > 0
    assert "cost_breakdown" in cost_data


@pytest.mark.asyncio
async def test_concurrent_quota_increment():
    """Simulate 20 concurrent workers atomically incrementing usage counter without race conditions."""
    org_id = "test_org_concurrent_workers_888"
    period = UsageService.current_period()

    async def _worker_task():
        for _ in range(5):
            await UsageCounterRepository.increment_counter(org_id, "certificates_generated", period, 1)

    # Launch 20 concurrent tasks, each incrementing 5 times -> total 100
    tasks = [_worker_task() for _ in range(20)]
    await asyncio.gather(*tasks)

    final_count = await UsageCounterRepository.get_counter(org_id, "certificates_generated", period)
    assert final_count == 100
