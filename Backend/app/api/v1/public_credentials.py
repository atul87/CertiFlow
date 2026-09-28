from __future__ import annotations
from typing import Dict, Any
from fastapi import APIRouter, Response, status
from app.schemas.common import APIResponse
from app.schemas.issuer import PublicIssuerProfileResponse
from app.schemas.credential import (
    PublicCredentialResponse,
    CredentialVerificationResponse,
    ExternalVerificationRequest,
)
from app.services.credential_service import CredentialService
from app.services.credential_issuer_service import CredentialIssuerService
from app.services.credential_verification_service import CredentialVerificationService
from app.services.credential_status_service import CredentialStatusService

router = APIRouter(prefix="/public", tags=["Public Digital Credentials"])


@router.get("/issuers/{issuer_id}", response_model=APIResponse[PublicIssuerProfileResponse])
async def get_public_issuer_profile(issuer_id: str):
    """Public resolution endpoint for issuer profile, metadata, and public verification keys."""
    profile = await CredentialIssuerService.get_public_issuer_profile(issuer_id)
    return APIResponse.ok(PublicIssuerProfileResponse(**profile))


@router.get("/credentials/{credential_id}", response_model=APIResponse[PublicCredentialResponse])
async def get_public_credential(credential_id: str):
    """
    Public, privacy-safe credential presentation.
    Opaque ID; exposes recipient name and achievement metadata while protecting personal emails and DB IDs.
    """
    cred = await CredentialService.get_public_credential(credential_id)
    return APIResponse.ok(PublicCredentialResponse(**cred))


@router.get("/credentials/{credential_id}/verify", response_model=APIResponse[CredentialVerificationResponse])
async def verify_credential(credential_id: str):
    """
    Live verification of cryptographic signature, issuer authenticity, expiration, and revocation status.
    """
    result = await CredentialVerificationService.verify_by_credential_id(credential_id)
    return APIResponse.ok(CredentialVerificationResponse(**result))


@router.get("/credentials/{credential_id}/badge")
async def get_open_badge_document(credential_id: str):
    """
    Returns 1EdTech / IMS Global / W3C Open Badges 3.0 compliant JSON-LD document.
    """
    badge_doc = await CredentialService.get_open_badge_json(credential_id)
    return Response(
        content=badge_doc if isinstance(badge_doc, str) else None,
        media_type="application/ld+json",
    ) if isinstance(badge_doc, str) else badge_doc


@router.get("/credentials/{credential_id}/vc")
async def get_w3c_vc_document(credential_id: str):
    """
    Returns W3C Verifiable Credentials Data Model v2.0 JSON document.
    """
    vc_doc = await CredentialService.get_w3c_vc_json(credential_id)
    return Response(
        content=vc_doc if isinstance(vc_doc, str) else None,
        media_type="application/ld+json",
    ) if isinstance(vc_doc, str) else vc_doc


@router.get("/credentials/{credential_id}/status")
async def get_credential_status(credential_id: str):
    """
    Returns real-time credential status list entry for independent verifiers.
    """
    status_doc = await CredentialStatusService.get_status(credential_id)
    return APIResponse.ok(status_doc)


@router.post("/credentials/verify", response_model=APIResponse[CredentialVerificationResponse])
async def verify_external_credential(body: ExternalVerificationRequest):
    """
    Independent standards-based verifier. Accepts arbitrary external W3C VC or Open Badges v3 JSON payloads,
    resolves keys, and validates cryptographic signatures independently of platform storage.
    """
    result = await CredentialVerificationService.verify_external_payload(body.credential_payload)
    return APIResponse.ok(CredentialVerificationResponse(**result))
