from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Request, status
from app.api.deps import get_current_user_and_org, require_role
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.common import APIResponse
from app.schemas.email import (
    EmailTemplateCreateRequest,
    EmailTemplateUpdateRequest,
    EmailTemplateResponse,
    EmailTemplateListResponse,
)
from app.repositories.email_template_repository import EmailTemplateRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.email_render_service import EmailRenderService

router = APIRouter(prefix="/email/templates", tags=["Email Templates"])


@router.post(
    "",
    response_model=APIResponse[EmailTemplateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create an email template",
)
async def create_email_template(
    data: EmailTemplateCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    # 1. Validate variables in subject, html_body, and text_body
    vars_subj = EmailRenderService.validate_template_variables(data.subject)
    vars_html = EmailRenderService.validate_template_variables(data.html_body)
    all_vars = sorted(list(set(vars_subj + vars_html)))

    # Fallback text body if not provided
    text_body = data.text_body or EmailRenderService.generate_plain_text(data.html_body)
    if data.text_body:
        vars_text = EmailRenderService.validate_template_variables(data.text_body)
        all_vars = sorted(list(set(all_vars + vars_text)))

    template = await EmailTemplateRepository.create(
        organization_id=org_id,
        name=data.name,
        subject=data.subject,
        html_body=data.html_body,
        text_body=text_body,
        variables=all_vars,
        created_by=user_id,
    )

    await AuditLogRepository.log_event(
        action="email_template.created",
        resource_type="email_template",
        resource_id=template["id"],
        organization_id=org_id,
        user_id=user_id,
        metadata={"name": data.name},
    )

    return APIResponse.ok(EmailTemplateResponse(**template))


@router.get(
    "",
    response_model=APIResponse[EmailTemplateListResponse],
    summary="List organization email templates",
)
async def list_email_templates(
    status_filter: Optional[str] = None,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    items = await EmailTemplateRepository.list_templates(org_id, status=status_filter)
    resp = EmailTemplateListResponse(
        items=[EmailTemplateResponse(**d) for d in items],
        total=len(items),
    )
    return APIResponse.ok(resp)


@router.get(
    "/{id}",
    response_model=APIResponse[EmailTemplateResponse],
    summary="Get an email template by ID",
)
async def get_email_template(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    template = await EmailTemplateRepository.get_by_id(id, org_id)
    if not template:
        raise NotFoundError(message="Email template not found", code="TEMPLATE_NOT_FOUND")
    return APIResponse.ok(EmailTemplateResponse(**template))


@router.put(
    "/{id}",
    response_model=APIResponse[EmailTemplateResponse],
    summary="Update an email template",
)
async def update_email_template(
    id: str,
    data: EmailTemplateUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    existing = await EmailTemplateRepository.get_by_id(id, org_id)
    if not existing:
        raise NotFoundError(message="Email template not found", code="TEMPLATE_NOT_FOUND")

    updates = {}
    if data.name is not None:
        updates["name"] = data.name
    if data.subject is not None:
        EmailRenderService.validate_template_variables(data.subject)
        updates["subject"] = data.subject
    if data.html_body is not None:
        EmailRenderService.validate_template_variables(data.html_body)
        updates["html_body"] = data.html_body
    if data.text_body is not None:
        EmailRenderService.validate_template_variables(data.text_body)
        updates["text_body"] = data.text_body
    if data.status is not None:
        updates["status"] = data.status

    # Re-evaluate variables if subject or html changed
    eff_subj = updates.get("subject", existing["subject"])
    eff_html = updates.get("html_body", existing["html_body"])
    eff_text = updates.get("text_body", existing.get("text_body", ""))
    vars_subj = EmailRenderService.extract_variables(eff_subj)
    vars_html = EmailRenderService.extract_variables(eff_html)
    vars_text = EmailRenderService.extract_variables(eff_text)
    updates["variables"] = sorted(list(set(vars_subj + vars_html + vars_text)))

    updated = await EmailTemplateRepository.update(id, org_id, updates)
    if not updated:
        raise NotFoundError(message="Email template not found", code="TEMPLATE_NOT_FOUND")

    await AuditLogRepository.log_event(
        action="email_template.updated",
        resource_type="email_template",
        resource_id=id,
        organization_id=org_id,
        user_id=user_id,
    )

    return APIResponse.ok(EmailTemplateResponse(**updated))


@router.delete(
    "/{id}",
    response_model=APIResponse[Dict[str, bool]],
    summary="Delete an email template",
)
async def delete_email_template(
    id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    success = await EmailTemplateRepository.delete(id, org_id)
    if not success:
        raise NotFoundError(message="Email template not found", code="TEMPLATE_NOT_FOUND")

    await AuditLogRepository.log_event(
        action="email_template.deleted",
        resource_type="email_template",
        resource_id=id,
        organization_id=org_id,
        user_id=user_id,
    )

    return APIResponse.ok({"deleted": True})
