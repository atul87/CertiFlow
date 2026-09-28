from __future__ import annotations
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.schemas.credential import (
    CredentialCreateRequest,
    CredentialRevokeRequest,
    CredentialResponse,
)
from app.services.credential_service import CredentialService

router = APIRouter(prefix="/credentials", tags=["Credentials"])


@router.post("", response_model=APIResponse[CredentialResponse], status_code=status.HTTP_201_CREATED)
async def issue_credential(
    body: CredentialCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    user_id = context["user"]["id"]
    evidence_dicts = [e.model_dump() for e in body.evidence] if body.evidence else None

    cred = await CredentialService.issue_credential_for_certificate(
        organization_id=org_id,
        certificate_id=body.certificate_id,
        achievement_id=body.achievement_id,
        valid_from=body.valid_from,
        expires_at=body.expires_at,
        evidence=evidence_dicts,
        actor_id=user_id
    )
    return APIResponse.created(CredentialResponse(**cred))


@router.get("", response_model=APIResponse[Dict[str, Any]])
async def list_credentials(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    achievement_id: Optional[str] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    items, total = await CredentialService.list_credentials(
        organization_id=org_id,
        skip=skip,
        limit=limit,
        status=status,
        achievement_id=achievement_id
    )
    return APIResponse.ok({
        "items": [CredentialResponse(**c) for c in items],
        "total": total,
        "skip": skip,
        "limit": limit
    })


@router.get("/{credential_id}", response_model=APIResponse[CredentialResponse])
async def get_credential(
    credential_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    cred = await CredentialService.get_credential_by_id(credential_id, org_id)
    return APIResponse.ok(CredentialResponse(**cred))


@router.post("/{credential_id}/revoke", response_model=APIResponse[CredentialResponse])
async def revoke_credential(
    credential_id: str,
    body: CredentialRevokeRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    user_id = context["user"]["id"]
    revoked = await CredentialService.revoke_credential(
        credential_id=credential_id,
        organization_id=org_id,
        reason=body.reason,
        actor_id=user_id
    )
    return APIResponse.ok(CredentialResponse(**revoked))


@router.post("/{credential_id}/suspend", response_model=APIResponse[CredentialResponse])
async def suspend_credential(
    credential_id: str,
    body: CredentialRevokeRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    user_id = context["user"]["id"]
    suspended = await CredentialService.suspend_credential(
        credential_id=credential_id,
        organization_id=org_id,
        reason=body.reason,
        actor_id=user_id
    )
    return APIResponse.ok(CredentialResponse(**suspended))


@router.post("/{credential_id}/restore", response_model=APIResponse[CredentialResponse])
async def restore_credential(
    credential_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    user_id = context["user"]["id"]
    restored = await CredentialService.restore_credential(
        credential_id=credential_id,
        organization_id=org_id,
        actor_id=user_id
    )
    return APIResponse.ok(CredentialResponse(**restored))
