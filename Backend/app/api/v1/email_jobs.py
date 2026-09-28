from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.schemas.email import (
    EmailJobCreateRequest,
    EmailJobResponse,
    EmailJobListResponse,
)
from app.services.email_job_service import EmailJobService

router = APIRouter(prefix="/email-jobs", tags=["Email Jobs"])


@router.post(
    "",
    response_model=APIResponse[EmailJobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create and start a bulk email job",
)
async def create_email_job(
    data: EmailJobCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    job = await EmailJobService.create_email_job(
        org_id=org_id,
        certificate_ids=data.certificate_ids,
        template_id=data.template_id,
        delivery_mode=data.delivery_mode.value,
        user_id=user_id,
    )
    return APIResponse.ok(EmailJobResponse(**job))


@router.get(
    "",
    response_model=APIResponse[EmailJobListResponse],
    summary="List bulk email jobs",
)
async def list_email_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    items, total = await EmailJobService.list_jobs(org_id, page, limit)
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    resp = EmailJobListResponse(
        items=[EmailJobResponse(**d) for d in items],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )
    return APIResponse.ok(resp)


@router.get(
    "/{id}",
    response_model=APIResponse[EmailJobResponse],
    summary="Get bulk email job details",
)
async def get_email_job(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    job = await EmailJobService.get_job(id, org_id)
    return APIResponse.ok(EmailJobResponse(**job))


@router.get(
    "/{id}/progress",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get bulk email job progress metrics",
)
async def get_email_job_progress(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    job = await EmailJobService.get_job(id, org_id)
    total = job.get("total", 0)
    sent = job.get("sent", 0)
    delivered = job.get("delivered", 0)
    failed = job.get("failed", 0)
    bounced = job.get("bounced", 0)
    processed = sent + failed + bounced
    percentage = round((processed / total * 100.0), 2) if total > 0 else 0.0

    return APIResponse.ok({
        "job_id": job["id"],
        "status": job["status"],
        "total": total,
        "processed": processed,
        "sent": sent,
        "delivered": delivered,
        "failed": failed,
        "bounced": bounced,
        "progress_percentage": percentage,
        "delivery_rate": round((delivered / total * 100.0), 2) if total > 0 else 0.0,
        "failure_rate": round((failed / total * 100.0), 2) if total > 0 else 0.0,
        "bounce_rate": round((bounced / total * 100.0), 2) if total > 0 else 0.0,
    })


@router.post(
    "/{id}/pause",
    response_model=APIResponse[EmailJobResponse],
    summary="Pause bulk email job",
)
async def pause_email_job(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]
    job = await EmailJobService.pause_job(id, org_id, user_id)
    return APIResponse.ok(EmailJobResponse(**job))


@router.post(
    "/{id}/resume",
    response_model=APIResponse[EmailJobResponse],
    summary="Resume bulk email job",
)
async def resume_email_job(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]
    job = await EmailJobService.resume_job(id, org_id, user_id)
    return APIResponse.ok(EmailJobResponse(**job))


@router.post(
    "/{id}/cancel",
    response_model=APIResponse[EmailJobResponse],
    summary="Cancel bulk email job",
)
async def cancel_email_job(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]
    job = await EmailJobService.cancel_job(id, org_id, user_id)
    return APIResponse.ok(EmailJobResponse(**job))
