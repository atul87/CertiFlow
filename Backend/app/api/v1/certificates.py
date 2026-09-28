"""
Certificates API — P3 Routes

POST   /certificates/preview              → render preview (no record created)
POST   /certificates/generate             → official generation
GET    /certificates                      → list certificates
GET    /certificates/{cert_id}            → get certificate
GET    /certificates/{cert_id}/pdf        → download PDF
GET    /certificates/{cert_id}/preview    → download preview PNG
POST   /certificates/{cert_id}/revoke     → revoke
GET    /verify/{code}                     → public verification (no auth)
"""
from typing import Dict, Any, Optional
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import StreamingResponse
import io

from app.api.deps import (
    get_current_user_and_org,
    require_role,
    get_client_ip,
    get_client_user_agent,
)
from app.core.exceptions import AppException
from app.schemas.common import APIResponse
from app.schemas.certificate import (
    CertificatePreviewRequest,
    CertificatePreviewResponse,
    CertificateGenerateRequest,
    CertificateResponse,
    CertificateListResponse,
    CertificateRevokeRequest,
    CertificateVerifyResponse,
)
from app.services.certificate_service import CertificateService
from app.repositories.certificate_repository import CertificateRepository

router = APIRouter(tags=["Certificates"])

# ---------------------------------------------------------------------------
# Preview (no persistent record)
# ---------------------------------------------------------------------------

@router.post(
    "/certificates/preview",
    response_model=APIResponse[CertificatePreviewResponse],
    summary="Render a certificate preview",
    description=(
        "Renders the certificate design with recipient data substituted as a "
        "base64 PNG. Does NOT create an official certificate record."
    ),
)
async def preview_certificate(
    data: CertificatePreviewRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["organization"]["id"]
    result = await CertificateService.preview(
        request=data,
        org_id=org_id,
        user_id=user["id"],
    )
    return APIResponse.ok(result)


# ---------------------------------------------------------------------------
# Official generation
# ---------------------------------------------------------------------------

@router.post(
    "/certificates/generate",
    response_model=APIResponse[CertificateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate an official certificate",
    description=(
        "Runs the full generation pipeline: validate → render → PDF → store → "
        "record.  Supports idempotency via the `Idempotency-Key` header."
    ),
)
async def generate_certificate(
    data: CertificateGenerateRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["organization"]["id"]
    idempotency_key: Optional[str] = request.headers.get("Idempotency-Key")
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    cert = await CertificateService.generate(
        request=data,
        org_id=org_id,
        user_id=user["id"],
        idempotency_key=idempotency_key,
        ip_address=ip,
        user_agent=ua,
    )
    return APIResponse.ok(cert)


# ---------------------------------------------------------------------------
# List certificates
# ---------------------------------------------------------------------------

@router.get(
    "/certificates",
    response_model=APIResponse[CertificateListResponse],
    summary="List certificates",
)
async def list_certificates(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    template_id: Optional[str] = Query(None),
    recipient_email: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["organization"]["id"]
    result = await CertificateService.list_certificates(
        org_id=org_id,
        page=page,
        limit=limit,
        status=status_filter,
        template_id=template_id,
        recipient_email=recipient_email,
        search=search,
    )
    return APIResponse.ok(CertificateListResponse(**result))


# ---------------------------------------------------------------------------
# Get single certificate
# ---------------------------------------------------------------------------

@router.get(
    "/certificates/{cert_id}",
    response_model=APIResponse[CertificateResponse],
    summary="Get certificate by ID",
)
async def get_certificate(
    cert_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["organization"]["id"]
    cert = await CertificateService.get_certificate(cert_id=cert_id, org_id=org_id)
    return APIResponse.ok(cert)


# ---------------------------------------------------------------------------
# Download PDF
# ---------------------------------------------------------------------------

@router.get(
    "/certificates/{cert_id}/pdf",
    summary="Download certificate PDF",
)
async def download_pdf(
    cert_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["organization"]["id"]
    pdf_bytes, filename = await CertificateService.get_pdf_bytes(cert_id=cert_id, org_id=org_id)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# Download preview PNG
# ---------------------------------------------------------------------------

@router.get(
    "/certificates/{cert_id}/preview",
    summary="Download certificate preview PNG",
)
async def download_preview(
    cert_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["organization"]["id"]
    preview_bytes = await CertificateService.get_preview_bytes(cert_id=cert_id, org_id=org_id)
    return StreamingResponse(
        io.BytesIO(preview_bytes),
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=preview_{cert_id}.png"},
    )


# ---------------------------------------------------------------------------
# Revoke
# ---------------------------------------------------------------------------

@router.post(
    "/certificates/{cert_id}/revoke",
    response_model=APIResponse[CertificateResponse],
    summary="Revoke a certificate",
)
async def revoke_certificate(
    cert_id: str,
    data: CertificateRevokeRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context["organization"]["id"]
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    cert = await CertificateService.revoke_certificate(
        cert_id=cert_id,
        org_id=org_id,
        user_id=user["id"],
        reason=data.reason,
        ip_address=ip,
        user_agent=ua,
    )
    return APIResponse.ok(cert)


# ---------------------------------------------------------------------------
# Public verification (no auth required) — P3.65
# ---------------------------------------------------------------------------

@router.get(
    "/verify/{code}",
    response_model=CertificateVerifyResponse,
    summary="Public certificate verification",
    description=(
        "Verifies a certificate using its verification code. "
        "Returns limited public information — no authentication required."
    ),
)
async def verify_certificate(code: str):
    doc = await CertificateRepository.get_by_verification_code(code.upper())
    if not doc or doc.get("status") == "revoked":
        return CertificateVerifyResponse(
            valid=False,
            status=doc.get("status") if doc else None,
            revoked_at=doc.get("revoked_at") if doc else None,
            revocation_reason=doc.get("revocation_reason") if doc else None,
        )
    return CertificateVerifyResponse(
        valid=True,
        certificate_number=doc.get("certificate_number"),
        recipient_name=doc.get("recipient", {}).get("name"),
        template_name=doc.get("template_snapshot", {}).get("template_name"),
        issued_at=doc.get("issued_at"),
        status=doc.get("status"),
    )
