from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics.cache_service import AnalyticsCacheService


class TemplateAnalyticsService:
    @classmethod
    async def get_analytics(
        cls,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        async def _compute():
            return await AnalyticsRepository.get_template_analytics(org_id, start_date, end_date)

        return await AnalyticsCacheService.get_or_set(
            org_id=org_id,
            category="templates",
            params={"start": str(start_date), "end": str(end_date)},
            compute_fn=_compute,
        )
