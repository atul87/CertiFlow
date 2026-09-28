"""
Reports API — P7 Routes

POST /reports                   → create background report job (CSV or PDF)
GET  /reports                   → list generated reports for the organization
GET  /reports/{report_id}        → get report details and download link
GET  /reports/{report_id}/download → download report with signed token / auth verification
"""
from __future__ import annotations
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import StreamingResponse
import io

from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.schemas.reports import (
    ReportJobCreateRequest,
    ReportJobResponse,
    ReportJobListResponse,
)
from app.services.reports.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=APIResponse[ReportJobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new report generation job",
)
async def create_report_job(
    request: ReportJobCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    filters = {
        **request.filters,
        "date_range": request.date_range,
        "from_date": request.from_date,
        "to_date": request.to_date,
    }

    job = await ReportService.create_report(
        org_id=org_id,
        report_type=request.type.value,
        format_type=request.format.value,
        filters=filters,
        user_id=user_id,
    )
    return APIResponse.ok(ReportJobResponse(**job))


@router.get(
    "",
    response_model=APIResponse[ReportJobListResponse],
    summary="List report generation jobs",
)
async def list_report_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    items, total = await ReportService.list_reports(org_id=org_id, page=page, limit=limit)
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return APIResponse.ok(ReportJobListResponse(
        items=[ReportJobResponse(**item) for item in items],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    ))


@router.get(
    "/{report_id}",
    response_model=APIResponse[ReportJobResponse],
    summary="Get report job status and download URL",
)
async def get_report_job(
    report_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    job = await ReportService.get_report(report_job_id=report_id, org_id=org_id)
    return APIResponse.ok(ReportJobResponse(**job))


@router.get(
    "/{report_id}/download",
    summary="Download report file via signed URL token or session auth",
)
async def download_report_file(
    report_id: str,
    token: Optional[str] = Query(None, description="Signed URL security token"),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    content_bytes, filename, media_type = await ReportService.get_report_file_bytes(
        report_job_id=report_id,
        org_id=org_id,
        token=token,
    )

    return StreamingResponse(
        io.BytesIO(content_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
