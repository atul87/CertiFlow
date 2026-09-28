"""
Analytics API — P7 Routes

GET  /analytics/dashboard       → organization dashboard with KPIs and deltas
GET  /analytics/certificates    → certificate lifecycle & issuance analytics
GET  /analytics/issuance        → bulk issuance job throughput and error insights
GET  /analytics/emails          → email delivery funnels, bounce rates, failure breakdown
GET  /analytics/verification    → verification attempts, validity trends, top scanned
GET  /analytics/templates       → template version usage & popularity distribution
GET  /analytics/imports         → recipient CSV/Excel import analytics
GET  /analytics/usage           → monthly quota usage and limits
GET  /analytics/storage         → storage consumption breakdown in MB
GET  /analytics/health          → platform operational health check (owner/admin)
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user_and_org, require_role
from app.schemas.common import APIResponse
from app.schemas.analytics import (
    DashboardOverviewResponse,
    CertificateAnalyticsResponse,
    IssuanceAnalyticsResponse,
    EmailAnalyticsResponse,
    VerificationAnalyticsResponse,
    TemplateAnalyticsResponse,
    ImportAnalyticsResponse,
    UsageAnalyticsResponse,
)
from app.services.analytics.dashboard_service import DashboardService
from app.services.analytics.certificate_analytics_service import CertificateAnalyticsService
from app.services.analytics.issuance_analytics_service import IssuanceAnalyticsService
from app.services.analytics.email_analytics_service import EmailAnalyticsService
from app.services.analytics.verification_analytics_service import VerificationAnalyticsService
from app.services.analytics.template_analytics_service import TemplateAnalyticsService
from app.services.analytics.usage_service import UsageService
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics.date_range_helper import DateRangeHelper
from app.core.database import DatabaseManager
from app.queue.redis import QueueManager
from app.core.config import settings
import os

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    response_model=APIResponse[DashboardOverviewResponse],
    summary="Get organization dashboard overview",
)
async def get_dashboard(
    preset: Optional[str] = Query("last_30_days", description="Preset date range or 'custom'"),
    from_date: Optional[datetime] = Query(None, description="Start date (ISO 8601) for custom range"),
    to_date: Optional[datetime] = Query(None, description="End date (ISO 8601) for custom range"),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await DashboardService.get_dashboard(
        org_id=org_id,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
    )
    return APIResponse.ok(DashboardOverviewResponse(**res))


@router.get(
    "/certificates",
    response_model=APIResponse[CertificateAnalyticsResponse],
    summary="Get certificate analytics",
)
async def get_certificate_analytics(
    preset: Optional[str] = Query("last_30_days"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await CertificateAnalyticsService.get_analytics(
        org_id=org_id,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
    )
    return APIResponse.ok(CertificateAnalyticsResponse(**res))


@router.get(
    "/issuance",
    response_model=APIResponse[IssuanceAnalyticsResponse],
    summary="Get issuance job analytics",
)
async def get_issuance_analytics(
    preset: Optional[str] = Query("last_30_days"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await IssuanceAnalyticsService.get_analytics(
        org_id=org_id,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
    )
    return APIResponse.ok(IssuanceAnalyticsResponse(**res))


@router.get(
    "/emails",
    response_model=APIResponse[EmailAnalyticsResponse],
    summary="Get email delivery analytics",
)
async def get_email_analytics(
    preset: Optional[str] = Query("last_30_days"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await EmailAnalyticsService.get_analytics(
        org_id=org_id,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
    )
    return APIResponse.ok(EmailAnalyticsResponse(**res))


@router.get(
    "/verification",
    response_model=APIResponse[VerificationAnalyticsResponse],
    summary="Get verification analytics",
)
async def get_verification_analytics(
    preset: Optional[str] = Query("last_30_days"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await VerificationAnalyticsService.get_analytics(
        org_id=org_id,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
    )
    return APIResponse.ok(VerificationAnalyticsResponse(**res))


@router.get(
    "/templates",
    response_model=APIResponse[TemplateAnalyticsResponse],
    summary="Get template analytics",
)
async def get_template_analytics(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await TemplateAnalyticsService.get_analytics(
        org_id=org_id,
        start_date=from_date,
        end_date=to_date,
    )
    return APIResponse.ok(TemplateAnalyticsResponse(**res))


@router.get(
    "/imports",
    response_model=APIResponse[ImportAnalyticsResponse],
    summary="Get recipient import analytics",
)
async def get_import_analytics(
    preset: Optional[str] = Query("last_30_days"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    start, end, _, _ = DateRangeHelper.resolve_range(preset=preset, from_date=from_date, to_date=to_date)
    res = await AnalyticsRepository.get_import_analytics(org_id, start, end)
    return APIResponse.ok(ImportAnalyticsResponse(**res))


@router.get(
    "/usage",
    response_model=APIResponse[UsageAnalyticsResponse],
    summary="Get monthly usage & quotas",
)
async def get_usage_analytics(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await UsageService.get_usage(org_id)
    return APIResponse.ok(UsageAnalyticsResponse(**res))


@router.get(
    "/storage",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get organization storage consumption breakdown",
)
async def get_storage_analytics(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await UsageService.get_storage(org_id)
    return APIResponse.ok(res)


@router.get(
    "/health",
    response_model=APIResponse[Dict[str, Any]],
    summary="Operational health check for platform services (Admin only)",
    dependencies=[Depends(require_role(["owner", "admin"]))],
)
async def get_operational_health(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    # 1. MongoDB check
    db_status = "healthy"
    try:
        db = DatabaseManager.get_db()
        await db.command("ping")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # 2. Redis check
    redis_status = "healthy"
    try:
        redis = await QueueManager.get_redis()
        if redis:
            await redis.ping()
        else:
            redis_status = "disconnected"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"

    # 3. Storage check
    storage_status = "healthy"
    try:
        os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    except Exception as e:
        storage_status = f"unhealthy: {str(e)}"

    # 4. Email check
    email_status = "healthy" if settings.EMAIL_PROVIDER or settings.APP_ENV in ("test", "development") else "unconfigured"

    return APIResponse.ok({
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "api": "healthy",
            "database": db_status,
            "redis": redis_status,
            "storage": storage_status,
            "email": email_status,
        }
    })
