from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.repositories.usage_counter_repository import UsageCounterRepository
from app.repositories.usage_event_repository import UsageEventRepository
from app.services.entitlement_service import EntitlementService
from app.schemas.usage import UsageSummaryResponse, UsageItemResponse


class UsageService:
    @staticmethod
    def current_period() -> str:
        """Standard monthly billing period string YYYY-MM (e.g. '2026-09')."""
        return datetime.now(timezone.utc).strftime("%Y-%m")

    @classmethod
    async def record_usage(
        cls,
        org_id: str,
        metric: str,
        quantity: int = 1,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ) -> int:
        """
        Record metered usage:
        1. Atomically increment aggregated monthly counter.
        2. Insert immutable usage audit log.
        Returns the updated counter quantity.
        """
        period = cls.current_period()
        new_val = await UsageCounterRepository.increment_counter(
            organization_id=org_id,
            metric=metric,
            period=period,
            quantity=quantity
        )
        event_meta = dict(metadata or {})
        if source:
            event_meta["source"] = source

        await UsageEventRepository.record_event(
            organization_id=org_id,
            metric=metric,
            quantity=quantity,
            period=period,
            resource_id=resource_id,
            metadata=event_meta
        )
        return new_val

    @classmethod
    async def set_gauge(
        cls,
        org_id: str,
        metric: str,
        quantity: int
    ) -> int:
        """Set absolute value for gauge metric (e.g. current storage bytes)."""
        period = cls.current_period()
        return await UsageCounterRepository.set_gauge(
            organization_id=org_id,
            metric=metric,
            period=period,
            quantity=quantity
        )

    @classmethod
    async def get_usage_summary(
        cls,
        org_id: str,
        period: Optional[str] = None
    ) -> UsageSummaryResponse:
        """
        Produce complete organization usage summary compared against plan limits.
        Computes percentages and warning flags (80%, 90%, 100%).
        """
        p = period or cls.current_period()
        counters = await UsageCounterRepository.get_all_for_period(org_id, p)
        plan = await EntitlementService.get_org_plan(org_id)
        entitlements = plan.get("entitlements", {})

        metrics_map: Dict[str, UsageItemResponse] = {}
        is_over_limit = False
        warning_messages = []

        # Key tracked quotas
        tracked_metrics = [
            ("certificates_generated", "max_certificates_monthly"),
            ("storage_bytes", "max_storage_bytes"),
            ("emails_sent", "max_certificates_monthly"),
            ("api_requests", None),
            ("imports_processed", None),
            ("webhook_deliveries", None),
        ]

        for metric_name, limit_field in tracked_metrics:
            used = counters.get(metric_name, 0)
            limit = -1
            if limit_field:
                limit = await EntitlementService.get_limit(org_id, limit_field)

            remaining = max(0, limit - used) if limit > 0 else -1
            pct = round((used / limit) * 100, 1) if limit > 0 else 0.0

            warning_level = None
            if limit > 0:
                if pct >= 100.0:
                    warning_level = "exceeded"
                    is_over_limit = True
                    warning_messages.append(f"Quota for {metric_name} reached 100% limit ({used}/{limit}).")
                elif pct >= 90.0:
                    warning_level = "critical"
                    warning_messages.append(f"Quota for {metric_name} is at {pct}% ({used}/{limit}).")
                elif pct >= 80.0:
                    warning_level = "warning"
                    warning_messages.append(f"Quota for {metric_name} is approaching limit at {pct}% ({used}/{limit}).")

            metrics_map[metric_name] = UsageItemResponse(
                used=used,
                limit=limit,
                remaining=remaining,
                usage_percentage=pct,
                warning_level=warning_level
            )

        return UsageSummaryResponse(
            organization_id=org_id,
            period=p,
            plan_id=plan.get("plan_id", "free"),
            metrics=metrics_map,
            is_over_limit=is_over_limit,
            warning_messages=warning_messages
        )
