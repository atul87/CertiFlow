from __future__ import annotations
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from app.services.reports.report_service import ReportService
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.analytics_daily_repository import AnalyticsDailyRepository

logger = logging.getLogger(__name__)


async def generate_report_task(
    ctx: Optional[Dict[str, Any]],
    report_job_id: str,
    org_id: str,
) -> Optional[Dict[str, Any]]:
    """ARQ background worker task to generate a CSV or PDF report."""
    logger.info(f"[ReportWorker] Starting report generation for job {report_job_id}, org {org_id}")
    try:
        res = await ReportService.process_report(report_job_id, org_id)
        logger.info(f"[ReportWorker] Finished report {report_job_id} with status {res.get('status') if res else 'failed'}")
        return res
    except Exception as e:
        logger.exception(f"[ReportWorker] Unhandled error generating report {report_job_id}: {e}")
        return None


async def aggregate_daily_analytics_task(
    ctx: Optional[Dict[str, Any]],
    org_id: str,
    target_date_str: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    ARQ background worker task to pre-aggregate daily analytics metrics
    into the analytics_daily collection.
    """
    now = datetime.now(timezone.utc)
    if target_date_str:
        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        # Default to yesterday
        target_dt = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    date_str = target_dt.strftime("%Y-%m-%d")
    start_dt = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = start_dt + timedelta(days=1) - timedelta(microseconds=1)

    logger.info(f"[ReportWorker] Aggregating daily analytics for org {org_id}, date {date_str}")
    try:
        kpis = await AnalyticsRepository.get_kpis(org_id, start_dt, end_dt)
        emails = await AnalyticsRepository.get_email_analytics(org_id, start_dt, end_dt)
        verif = await AnalyticsRepository.get_verification_analytics(org_id, start_dt, end_dt)

        metrics = {
            "certificates": {
                "issued": kpis.get("certificates_issued", 0),
                "active": kpis.get("active_certificates", 0),
                "revoked": kpis.get("revoked_certificates", 0),
            },
            "emails": {
                "sent": emails.get("sent", 0),
                "delivered": emails.get("delivered", 0),
                "failed": emails.get("failed", 0),
                "bounced": emails.get("bounced", 0),
            },
            "verification": {
                "total": verif.get("total_attempts", 0),
                "successful": verif.get("successful_valid", 0),
                "revoked": verif.get("revoked", 0),
                "expired": verif.get("expired", 0),
                "not_found": verif.get("not_found_or_invalid", 0),
            },
        }

        saved = await AnalyticsDailyRepository.upsert_daily(org_id, date_str, metrics)
        logger.info(f"[ReportWorker] Successfully saved daily analytics for org {org_id} on {date_str}")
        return saved
    except Exception as e:
        logger.exception(f"[ReportWorker] Failed to aggregate daily analytics for org {org_id}: {e}")
        return None
