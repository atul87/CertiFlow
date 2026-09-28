from __future__ import annotations
import io
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user_and_org
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.common import APIResponse
from app.schemas.issuance import (
    IssuanceJobCreateRequest,
    IssuanceJobResponse,
    IssuanceJobProgressResponse,
    IssuanceItemResponse,
    IssuanceItemListResponse,
    IssuanceJobListResponse,
    ZipStatusResponse,
    ErrorRowItem,
)
from app.services.issuance_service import IssuanceService
from app.services.progress_service import ProgressService
from app.services.zip_service import ZipService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/issuance-jobs", tags=["Issuance Jobs"])


@router.post(
    "",
    response_model=APIResponse[IssuanceJobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create and queue a bulk certificate issuance job",
)
async def create_issuance_job(
    data: IssuanceJobCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["org_id"]
    job = await IssuanceService.create_job(
        request=data,
        org_id=org_id,
        user_id=user["id"],
    )
    return APIResponse.ok(job)


@router.get(
    "",
    response_model=APIResponse[IssuanceJobListResponse],
    summary="List issuance jobs for current organization",
)
async def list_issuance_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    result = await IssuanceService.list_jobs(
        org_id=org_id,
        page=page,
        limit=limit,
        status=status,
    )
    return APIResponse.ok(result)


@router.get(
    "/{job_id}",
    response_model=APIResponse[IssuanceJobResponse],
    summary="Get details of an issuance job",
)
async def get_issuance_job(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    job = await IssuanceService.get_job(job_id, org_id)
    return APIResponse.ok(job)


@router.get(
    "/{job_id}/progress",
    response_model=APIResponse[IssuanceJobProgressResponse],
    summary="Get real-time progress of an issuance job",
)
async def get_issuance_job_progress(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    prog = await ProgressService.get_progress(job_id, org_id)
    return APIResponse.ok(prog)


@router.post(
    "/{job_id}/pause",
    response_model=APIResponse[IssuanceJobResponse],
    summary="Pause a processing issuance job",
)
async def pause_issuance_job(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["org_id"]
    job = await IssuanceService.pause_job(job_id, org_id, user["id"])
    return APIResponse.ok(job)


@router.post(
    "/{job_id}/resume",
    response_model=APIResponse[IssuanceJobResponse],
    summary="Resume a paused issuance job",
)
async def resume_issuance_job(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["org_id"]
    job = await IssuanceService.resume_job(job_id, org_id, user["id"])
    return APIResponse.ok(job)


@router.post(
    "/{job_id}/cancel",
    response_model=APIResponse[IssuanceJobResponse],
    summary="Cancel an issuance job (does not delete already generated certificates)",
)
async def cancel_issuance_job(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["org_id"]
    job = await IssuanceService.cancel_job(job_id, org_id, user["id"])
    return APIResponse.ok(job)


@router.post(
    "/{job_id}/retry-failed",
    response_model=APIResponse[IssuanceJobResponse],
    summary="Retry all failed items in an issuance job",
)
async def retry_failed_items(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["org_id"]
    job = await IssuanceService.retry_failed(job_id, org_id, user["id"])
    return APIResponse.ok(job)


@router.post(
    "/{job_id}/items/{item_id}/retry",
    response_model=APIResponse[IssuanceItemResponse],
    summary="Retry a single failed item in an issuance job",
)
async def retry_single_item(
    job_id: str,
    item_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["org_id"]
    item = await IssuanceService.retry_single_item(job_id, item_id, org_id, user["id"])
    return APIResponse.ok(item)


@router.get(
    "/{job_id}/items",
    response_model=APIResponse[IssuanceItemListResponse],
    summary="List items for an issuance job with filters",
)
async def list_job_items(
    job_id: str,
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    items = await IssuanceService.list_items(
        job_id=job_id,
        org_id=org_id,
        status=status,
        search=search,
        page=page,
        limit=limit,
    )
    return APIResponse.ok(items)


@router.get(
    "/{job_id}/errors",
    response_model=APIResponse[List[ErrorRowItem]],
    summary="Get error details for failed items in an issuance job",
)
async def get_job_errors(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    errors = await IssuanceService.get_errors(job_id, org_id)
    return APIResponse.ok(errors)


@router.get(
    "/{job_id}/errors/download",
    summary="Download issuance errors CSV report",
)
async def download_job_errors_csv(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    csv_content = await IssuanceService.generate_errors_csv(job_id, org_id)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="issuance-errors-{job_id}.csv"'
        }
    )


@router.post(
    "/{job_id}/zip",
    response_model=APIResponse[ZipStatusResponse],
    summary="Request a ZIP export of all certificates generated by this job",
)
async def request_job_zip(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["org_id"]
    res = await ZipService.request_zip(job_id, org_id, user["id"])
    return APIResponse.ok(res)


@router.get(
    "/{job_id}/zip",
    response_model=APIResponse[ZipStatusResponse],
    summary="Check status of certificate ZIP export",
)
async def get_job_zip_status(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    res = await ZipService.get_zip_status(job_id, org_id)
    return APIResponse.ok(res)


@router.get(
    "/{job_id}/zip/download",
    summary="Download generated ZIP archive of certificates",
)
async def download_job_zip(
    job_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    status_res = await ZipService.get_zip_status(job_id, org_id)
    if status_res.status != "ready":
        raise ValidationError(
            message=f"ZIP archive is not ready (current status: {status_res.status})",
            code="ZIP_NOT_READY",
        )

    zip_file_path = Path(StorageService.get_base_dir()) / "zips" / org_id / job_id / "certificates.zip"
    if not zip_file_path.exists():
        raise NotFoundError(message="ZIP file not found on storage", code="ZIP_NOT_FOUND")

    file_bytes = zip_file_path.read_bytes()
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="certificates-{job_id}.zip"'
        }
    )
