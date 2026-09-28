from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics.date_range_helper import DateRangeHelper
from app.services.analytics.cache_service import AnalyticsCacheService


class CertificateAnalyticsService:
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
            status_dist = await AnalyticsRepository.get_certificate_status_distribution(org_id, start, end)
            total_issued = status_dist["active"] + status_dist["revoked"] + status_dist["expired"]

            trend_raw = await AnalyticsRepository.get_certificate_issuance_trend(org_id, start, end)
            labels = [t["date"] for t in trend_raw]
            values = [t["count"] for t in trend_raw]
            trend_chart = {
                "labels": labels,
                "datasets": [{"name": "Issued", "values": values}]
            }

            by_template = await AnalyticsRepository.get_issuance_by_template(org_id, start, end)
            by_program = await AnalyticsRepository.get_issuance_by_program(org_id, start, end)

            return {
                "period": {
                    "start_date": start,
                    "end_date": end,
                    "preset": preset if not (from_date and to_date) else "custom",
                },
                "total_issued": total_issued,
                "active_count": status_dist["active"],
                "revoked_count": status_dist["revoked"],
                "expired_count": status_dist["expired"],
                "issuance_trend": trend_chart,
                "by_template": by_template,
                "by_program": by_program,
            }

        return await AnalyticsCacheService.get_or_set(
            org_id=org_id,
            category="certificates",
            params={"preset": preset, "from": str(start), "to": str(end)},
            compute_fn=_compute,
        )

    @classmethod
    async def search(
        cls,
        org_id: str,
        query: Optional[str] = None,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        program: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await AnalyticsRepository.search_certificates(
            org_id=org_id,
            query=query,
            status=status,
            template_id=template_id,
            program=program,
            start_date=from_date,
            end_date=to_date,
            page=page,
            limit=limit,
        )
