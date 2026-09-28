from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
import asyncio

from app.api.deps import get_current_user_and_org
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.common import APIResponse
from app.schemas.email import (
    EmailDeliveryResponse,
    EmailDeliveryListResponse,
)
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.repositories.email_event_repository import EmailEventRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.queue.redis import QueueManager
from app.queue.tasks import TASK_SEND_CERTIFICATE_EMAIL
from app.workers.email_worker import send_certificate_email_task

router = APIRouter(prefix="/email-deliveries", tags=["Email Deliveries"])


@router.get(
    "",
    response_model=APIResponse[EmailDeliveryListResponse],
    summary="List email deliveries with filtering and pagination",
)
async def list_email_deliveries(
    certificate_id: Optional[str] = None,
    email_job_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    items, total = await EmailDeliveryRepository.list_deliveries(
        organization_id=org_id,
        certificate_id=certificate_id,
        email_job_id=email_job_id,
        status=status_filter,
        page=page,
        limit=limit,
    )
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    resp = EmailDeliveryListResponse(
        items=[EmailDeliveryResponse(**d) for d in items],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )
    return APIResponse.ok(resp)


@router.get(
    "/{id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get email delivery detail with events timeline",
)
async def get_email_delivery(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    delivery = await EmailDeliveryRepository.get_by_id(id, org_id)
    if not delivery:
        raise NotFoundError(message="Email delivery not found", code="DELIVERY_NOT_FOUND")

    events = await EmailEventRepository.get_events_for_delivery(id)

    delivery_data = EmailDeliveryResponse(**delivery).model_dump()
    delivery_data["events"] = events
    return APIResponse.ok(delivery_data)


@router.post(
    "/{id}/retry",
    response_model=APIResponse[EmailDeliveryResponse],
    summary="Retry a failed email delivery",
)
async def retry_email_delivery(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    delivery = await EmailDeliveryRepository.get_by_id(id, org_id)
    if not delivery:
        raise NotFoundError(message="Email delivery not found", code="DELIVERY_NOT_FOUND")

    if delivery["status"] not in ("failed", "bounced"):
        raise ValidationError(message=f"Cannot retry delivery in status {delivery['status']}", code="INVALID_STATUS")

    reset = await EmailDeliveryRepository.reset_for_retry(id)
    if not reset:
        raise ValidationError(message="Failed to reset delivery for retry", code="RESET_FAILED")

    await AuditLogRepository.log_event(
        action="email_delivery.retry",
        resource_type="email_delivery",
        resource_id=id,
        organization_id=org_id,
        user_id=user_id,
    )

    queued = await QueueManager.enqueue(TASK_SEND_CERTIFICATE_EMAIL, id)
    if not queued and settings.APP_ENV != "test":
        asyncio.create_task(send_certificate_email_task(None, id))

    return APIResponse.ok(EmailDeliveryResponse(**reset))
