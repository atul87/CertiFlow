"""
Activity API — P7 Routes

GET /activity → Paginated audit and activity feed for the organization
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.repositories.audit_log_repository import AuditLogRepository

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get(
    "",
    response_model=APIResponse[Dict[str, Any]],
    summary="List organization activity and audit events",
)
async def list_activity(
    action: Optional[str] = Query(None, description="Filter by action name (e.g. certificate.generated)"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g. certificate, report_job)"),
    user_id: Optional[str] = Query(None, description="Filter by actor user ID"),
    from_date: Optional[datetime] = Query(None, description="Filter start date"),
    to_date: Optional[datetime] = Query(None, description="Filter end date"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]

    items, total = await AuditLogRepository.list_activity(
        organization_id=org_id,
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        start_date=from_date,
        end_date=to_date,
        page=page,
        limit=limit,
    )
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return APIResponse.ok({
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    })
