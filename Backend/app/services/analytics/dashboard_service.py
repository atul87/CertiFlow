from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.analytics.date_range_helper import DateRangeHelper
from app.services.analytics.cache_service import AnalyticsCacheService


class DashboardService:
    @classmethod
    async def get_dashboard(
        cls,
        org_id: str,
        preset: Optional[str] = "last_30_days",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        start, end, prev_start, prev_end = DateRangeHelper.resolve_range(
            preset=preset,
            from_date=from_date,
            to_date=to_date,
        )

        async def _compute():
            # 1. Fetch current & previous period KPIs
            current_kpis = await AnalyticsRepository.get_kpis(org_id, start, end)
            prev_kpis = await AnalyticsRepository.get_kpis(org_id, prev_start, prev_end)

            def _card(cur_val, prev_val):
                return {
                    "value": cur_val,
                    "previous_value": prev_val,
                    "change_percentage": DateRangeHelper.calculate_change_percentage(cur_val, prev_val),
                }

            cur_sent = current_kpis["emails_sent"]
            cur_deliv = current_kpis["emails_delivered"]
            cur_rate = round((cur_deliv / cur_sent * 100.0), 1) if cur_sent > 0 else 0.0

            prev_sent = prev_kpis["emails_sent"]
            prev_deliv = prev_kpis["emails_delivered"]
            prev_rate = round((prev_deliv / prev_sent * 100.0), 1) if prev_sent > 0 else 0.0

            kpis = {
                "certificates_issued": _card(current_kpis["certificates_issued"], prev_kpis["certificates_issued"]),
                "active_certificates": _card(current_kpis["active_certificates"], prev_kpis["active_certificates"]),
                "revoked_certificates": _card(current_kpis["revoked_certificates"], prev_kpis["revoked_certificates"]),
                "emails_sent": _card(cur_sent, prev_sent),
                "emails_delivered": _card(cur_deliv, prev_deliv),
                "delivery_rate": _card(cur_rate, prev_rate),
                "verifications_successful": _card(current_kpis["verifications_successful"], prev_kpis["verifications_successful"]),
                "failed_operations": _card(current_kpis["failed_operations"], prev_kpis["failed_operations"]),
            }

            # 2. Issuance trend chart
            trend_raw = await AnalyticsRepository.get_certificate_issuance_trend(org_id, start, end)
            labels = [t["date"] for t in trend_raw]
            values = [t["count"] for t in trend_raw]
            issuance_trend = {
                "labels": labels,
                "datasets": [{"name": "Certificates Issued", "values": values}]
            }

            # 3. Status distribution
            status_distribution = await AnalyticsRepository.get_certificate_status_distribution(org_id, start, end)

            # 4. Recent jobs & activity
            recent_jobs = await AnalyticsRepository.get_recent_jobs(org_id, limit=5)
            recent_activities, _ = await AuditLogRepository.list_activity(org_id, limit=6)

            return {
                "period": {
                    "start_date": start,
                    "end_date": end,
                    "preset": preset if not (from_date and to_date) else "custom",
                },
                "kpis": kpis,
                "issuance_trend": issuance_trend,
                "status_distribution": status_distribution,
                "recent_jobs": recent_jobs,
                "recent_activities": recent_activities,
            }

        return await AnalyticsCacheService.get_or_set(
            org_id=org_id,
            category="dashboard",
            params={"preset": preset, "from": str(start), "to": str(end)},
            compute_fn=_compute,
        )
