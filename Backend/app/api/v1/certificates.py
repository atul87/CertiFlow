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
from datetime import datetime
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
from app.schemas.email import (
    SendCertificateEmailRequest,
    EmailDeliveryResponse,
)
from app.services.certificate_service import CertificateService
from app.services.email_service import EmailService
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
    summary="List certificates with advanced search & filters",
)
async def list_certificates(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    template_id: Optional[str] = Query(None),
    recipient_email: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    program: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="issued_from"),
    to_date: Optional[datetime] = Query(None, alias="issued_to"),
    verification_code: Optional[str] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    result = await CertificateService.list_certificates(
        org_id=org_id,
        page=page,
        limit=limit,
        status=status_filter,
        template_id=template_id,
        recipient_email=recipient_email,
        search=search,
        program=program,
        from_date=from_date,
        to_date=to_date,
        verification_code=verification_code,
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

from app.services.verification_service import VerificationService
from app.repositories.verification_event_repository import VerificationEventRepository
from app.schemas.verification import (
    BulkRevokeRequest,
    BulkRevokeResponse,
    IntegrityCheckResponse,
    CertificateTimelineResponse,
    VerificationEventResponse,
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
    org_id = context.get("org_id") or context["organization"]["id"]
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    cert = await VerificationService.revoke_certificate(
        cert_id=cert_id,
        org_id=org_id,
        user_id=user["id"],
        reason=data.reason,
        ip_address=ip,
        user_agent=ua,
    )
    return APIResponse.ok(cert)


# ---------------------------------------------------------------------------
# Restore (P5.14)
# ---------------------------------------------------------------------------

@router.post(
    "/certificates/{cert_id}/restore",
    response_model=APIResponse[CertificateResponse],
    summary="Restore a revoked certificate to active status",
)
async def restore_certificate(
    cert_id: str,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context.get("org_id") or context["organization"]["id"]
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    cert = await VerificationService.restore_certificate(
        cert_id=cert_id,
        org_id=org_id,
        user_id=user["id"],
        ip_address=ip,
        user_agent=ua,
    )
    return APIResponse.ok(cert)


# ---------------------------------------------------------------------------
# Bulk Revoke (P5.47 / P5.48)
# ---------------------------------------------------------------------------

@router.post(
    "/certificates/bulk-revoke",
    response_model=APIResponse[BulkRevokeResponse],
    summary="Bulk revoke multiple certificates",
)
async def bulk_revoke_certificates(
    data: BulkRevokeRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user = context["user"]
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await VerificationService.bulk_revoke(
        cert_ids=data.certificate_ids,
        org_id=org_id,
        user_id=user["id"],
        reason=data.reason,
        notes=data.notes,
    )
    return APIResponse.ok(res)


# ---------------------------------------------------------------------------
# Integrity Verification (P5.17 - P5.19)
# ---------------------------------------------------------------------------

@router.get(
    "/certificates/{cert_id}/integrity",
    response_model=APIResponse[IntegrityCheckResponse],
    summary="Verify cryptographic SHA-256 integrity of stored certificate PDF",
)
async def check_certificate_integrity(
    cert_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    res = await VerificationService.check_integrity(cert_id, org_id)
    return APIResponse.ok(res)


# ---------------------------------------------------------------------------
# Certificate Timeline (P5.30)
# ---------------------------------------------------------------------------

@router.get(
    "/certificates/{cert_id}/timeline",
    response_model=APIResponse[CertificateTimelineResponse],
    summary="Get complete unified lifecycle, audit, delivery, and scan timeline for a certificate",
)
async def get_certificate_timeline(
    cert_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    from app.services.analytics.timeline_service import CertificateTimelineService
    res = await CertificateTimelineService.build_timeline(cert_id, org_id)
    return APIResponse.ok(CertificateTimelineResponse(**res))


# ---------------------------------------------------------------------------
# Verification Events History (P5.22 / P5.53)
# ---------------------------------------------------------------------------

@router.get(
    "/certificates/{cert_id}/verification-events",
    response_model=APIResponse[List[VerificationEventResponse]],
    summary="List verification scans for a certificate",
)
async def get_certificate_verification_events(
    cert_id: str,
    limit: int = Query(50, ge=1, le=200),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    events = await VerificationEventRepository.list_by_certificate(cert_id, limit=limit)
    return APIResponse.ok([VerificationEventResponse(**e) for e in events])


# ---------------------------------------------------------------------------
# Public verification (no auth required) — P3.65 / P5.05
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
async def verify_certificate(code: str, request: Request):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    result = await VerificationService.verify_by_code(code, user_agent=ua, ip_address=ip)
    if not result.valid:
        return CertificateVerifyResponse(
            valid=False,
            status=result.status,
            revoked_at=result.revoked_at,
            revocation_reason=result.revocation_reason,
        )
    return CertificateVerifyResponse(
        valid=True,
        certificate_number=result.certificate.certificate_number if result.certificate else None,
        recipient_name=result.certificate.recipient_name if result.certificate else None,
        template_name=result.certificate.program_name if result.certificate else None,
        issued_at=None,
        status=result.status,
    )


# ---------------------------------------------------------------------------
# Certificate Email Delivery (P6.22 / P6.46)
# ---------------------------------------------------------------------------

@router.post(
    "/certificates/{cert_id}/email",
    response_model=APIResponse[EmailDeliveryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send certificate by email",
)
async def send_certificate_email(
    cert_id: str,
    data: Optional[SendCertificateEmailRequest] = None,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    template_id = data.template_id if data else None
    delivery_mode = data.delivery_mode.value if data else "link"
    recipient_email = data.recipient_email if data else None

    delivery = await EmailService.send_certificate_email(
        certificate_id=cert_id,
        org_id=org_id,
        template_id=template_id,
        delivery_mode=delivery_mode,
        recipient_email_override=recipient_email,
        user_id=user_id,
    )
    return APIResponse.ok(EmailDeliveryResponse(**delivery))


@router.post(
    "/certificates/{cert_id}/resend-email",
    response_model=APIResponse[EmailDeliveryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Resend certificate by email",
)
async def resend_certificate_email(
    cert_id: str,
    data: Optional[SendCertificateEmailRequest] = None,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context.get("org_id") or context["organization"]["id"]
    user_id = context.get("user_id") or context["user"]["id"]

    template_id = data.template_id if data else None
    delivery_mode = data.delivery_mode.value if data else "link"
    recipient_email = data.recipient_email if data else None

    delivery = await EmailService.resend_certificate_email(
        certificate_id=cert_id,
        org_id=org_id,
        template_id=template_id,
        delivery_mode=delivery_mode,
        recipient_email_override=recipient_email,
        user_id=user_id,
    )
    return APIResponse.ok(EmailDeliveryResponse(**delivery))

