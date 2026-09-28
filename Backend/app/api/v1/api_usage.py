from __future__ import annotations
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_user_and_org,
    require_permission,
)
from app.schemas.common import APIResponse
from app.schemas.api_usage import APIUsageMetricsResponse
from app.services.api_usage_service import APIUsageService

router = APIRouter(prefix="/api-usage", tags=["API Usage"])


@router.get(
    "",
    response_model=APIResponse[APIUsageMetricsResponse],
    summary="Get API usage metrics, request totals, error rates, and latency breakdowns",
    dependencies=[Depends(require_permission("analytics.read"))],
)
async def get_api_usage(
    days: int = Query(30, ge=1, le=365),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    metrics = await APIUsageService.get_usage_metrics(
        org_id=org_id,
        days=days,
        start_date=start_date,
        end_date=end_date,
    )
    return APIResponse.ok(metrics)
