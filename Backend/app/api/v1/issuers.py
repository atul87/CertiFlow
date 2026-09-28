from __future__ import annotations
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.schemas.issuer import (
    IssuerProfileCreateRequest,
    IssuerProfileUpdateRequest,
    IssuerProfileResponse,
)
from app.services.credential_issuer_service import CredentialIssuerService

router = APIRouter(prefix="/issuers", tags=["Issuers"])


@router.get("/profile", response_model=APIResponse[IssuerProfileResponse])
async def get_issuer_profile(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    issuer = await CredentialIssuerService.get_issuer_by_org(org_id)
    return APIResponse.ok(IssuerProfileResponse(**issuer))


@router.put("/profile", response_model=APIResponse[IssuerProfileResponse])
async def update_issuer_profile(
    body: IssuerProfileUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    updated = await CredentialIssuerService.update_issuer(org_id, body)
    return APIResponse.ok(IssuerProfileResponse(**updated))


@router.post("/keys/rotate", response_model=APIResponse[Dict[str, Any]])
async def rotate_signing_keys(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    new_key = await CredentialIssuerService.rotate_keys(org_id)
    return APIResponse.ok({
        "key_id": new_key["key_id"],
        "algorithm": new_key["algorithm"],
        "status": new_key["status"],
        "message": "New active Ed25519 signing key provisioned. Historical keys retained for verification."
    })
