from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, EmailStr
from app.api.deps import get_current_user_and_org, require_role
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.schemas.common import APIResponse
from app.schemas.email import (
    EmailSettingsResponse,
    EmailSettingsUpdateRequest,
    EmailPreviewRequest,
    EmailPreviewResponse,
    EmailTestRequest,
    EmailSuppressionResponse,
)
from app.repositories.email_settings_repository import EmailSettingsRepository
from app.repositories.email_suppression_repository import EmailSuppressionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.email_service import EmailService

router = APIRouter(prefix="/email", tags=["Email Operations & Settings"])


# --- Email Settings ---

@router.get(
    "/settings",
    response_model=APIResponse[EmailSettingsResponse],
    summary="Get organization email settings",
)
async def get_email_settings(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    settings_doc = await EmailSettingsRepository.get_by_org(org_id)
    safe = EmailSettingsRepository.to_safe_response(settings_doc, org_id)
    return APIResponse.ok(EmailSettingsResponse(**safe))


@router.put(
    "/settings",
    response_model=APIResponse[EmailSettingsResponse],
    summary="Update organization email settings",
)
async def update_email_settings(
    data: EmailSettingsUpdateRequest,
    _role: str = Depends(require_role(["owner", "admin"])),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    updates = data.model_dump(exclude_unset=True)
    updated = await EmailSettingsRepository.upsert(org_id, updates)

    await AuditLogRepository.log_event(
        action="email_provider.updated",
        resource_type="email_settings",
        resource_id=org_id,
        organization_id=org_id,
        user_id=user_id,
        metadata={"provider": updated.get("provider")},
    )

    safe = EmailSettingsRepository.to_safe_response(updated, org_id)
    return APIResponse.ok(EmailSettingsResponse(**safe))


# --- Preview & Test ---

@router.post(
    "/preview",
    response_model=APIResponse[EmailPreviewResponse],
    summary="Preview rendered email",
)
async def preview_email(
    data: EmailPreviewRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    result = await EmailService.preview_email(
        org_id=org_id,
        template_id=data.template_id,
        certificate_id=data.certificate_id,
        subject_override=data.subject,
        html_override=data.html_body,
    )
    return APIResponse.ok(EmailPreviewResponse(**result))


@router.post(
    "/test",
    response_model=APIResponse[Dict[str, Any]],
    summary="Send test email",
)
async def send_test_email(
    data: EmailTestRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    result = await EmailService.send_test_email(
        org_id=org_id,
        recipient_email=data.recipient_email,
        template_id=data.template_id,
        user_id=user_id,
    )
    return APIResponse.ok(result)


# --- Suppression List ---

class AddSuppressionRequest(BaseModel):
    email: EmailStr
    reason: str = "manual"


@router.get(
    "/suppressions",
    response_model=APIResponse[Dict[str, Any]],
    summary="List organization email suppressions",
)
async def list_suppressions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    items, total = await EmailSuppressionRepository.list_suppressions(org_id, page, limit)
    return APIResponse.ok({
        "items": [EmailSuppressionResponse(**d) for d in items],
        "total": total,
        "page": page,
        "limit": limit,
    })


@router.post(
    "/suppressions",
    response_model=APIResponse[EmailSuppressionResponse],
    summary="Add email to suppression list",
)
async def add_suppression(
    data: AddSuppressionRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    doc = await EmailSuppressionRepository.add_suppression(
        organization_id=org_id,
        email=data.email,
        reason=data.reason,
    )
    await AuditLogRepository.log_event(
        action="email_suppression.added",
        resource_type="email_suppression",
        resource_id=doc["id"],
        organization_id=org_id,
        user_id=user_id,
        metadata={"email": data.email, "reason": data.reason},
    )
    return APIResponse.ok(EmailSuppressionResponse(**doc))


@router.delete(
    "/suppressions/{email}",
    response_model=APIResponse[Dict[str, bool]],
    summary="Remove email from suppression list",
)
async def remove_suppression(
    email: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    removed = await EmailSuppressionRepository.remove_suppression(org_id, email)
    if not removed:
        raise NotFoundError(message="Suppression not found", code="NOT_FOUND")

    await AuditLogRepository.log_event(
        action="email_suppression.removed",
        resource_type="email_suppression",
        resource_id=email,
        organization_id=org_id,
        user_id=user_id,
    )
    return APIResponse.ok({"removed": True})
