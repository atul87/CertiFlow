from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.repositories.api_usage_repository import APIUsageRepository
from app.schemas.api_usage import APIUsageMetricsResponse


class APIUsageService:
    @staticmethod
    async def get_usage_metrics(
        org_id: str,
        days: int = 30,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> APIUsageMetricsResponse:
        now = datetime.now(timezone.utc)
        if not end_date:
            end_date = now
        if not start_date:
            start_date = end_date - timedelta(days=days)

        metrics = await APIUsageRepository.get_metrics(
            org_id=org_id,
            start_date=start_date,
            end_date=end_date,
        )
        return APIUsageMetricsResponse(**metrics)
