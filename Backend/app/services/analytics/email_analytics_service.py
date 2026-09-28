from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics.date_range_helper import DateRangeHelper
from app.services.analytics.cache_service import AnalyticsCacheService


class EmailAnalyticsService:
    @classmethod
    async def get_analytics(
        cls,
        org_id: str,
        preset: Optional[str] = "last_30_days",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        start, end, _, _ = DateRangeHelper.resolve_range(
            preset=preset,
            from_date=from_date,
            to_date=to_date,
        )

        async def _compute():
            metrics = await AnalyticsRepository.get_email_analytics(org_id, start, end)
            return {
                "period": {
                    "start_date": start,
                    "end_date": end,
                    "preset": preset if not (from_date and to_date) else "custom",
                },
                **metrics,
            }

        return await AnalyticsCacheService.get_or_set(
            org_id=org_id,
            category="email",
            params={"preset": preset, "from": str(start), "to": str(end)},
            compute_fn=_compute,
        )
