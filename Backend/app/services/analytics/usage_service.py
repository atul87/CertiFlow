from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any

from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics.date_range_helper import DateRangeHelper
from app.services.analytics.cache_service import AnalyticsCacheService


class UsageService:
    @classmethod
    async def get_usage(cls, org_id: str) -> Dict[str, Any]:
        start, end, _, _ = DateRangeHelper.resolve_range(preset="this_month")

        async def _compute():
            return await AnalyticsRepository.get_usage_metrics(org_id, start, end)

        return await AnalyticsCacheService.get_or_set(
            org_id=org_id,
            category="usage",
            params={"month": start.strftime("%Y-%m")},
            compute_fn=_compute,
        )

    @classmethod
    async def get_storage(cls, org_id: str) -> Dict[str, Any]:
        return await AnalyticsRepository.get_storage_metrics(org_id)
