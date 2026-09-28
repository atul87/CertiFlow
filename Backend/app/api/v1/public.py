from __future__ import annotations
import io
from typing import Dict, Any, Optional
from fastapi import (
    APIRouter,
    Request,
    Response,
    UploadFile,
    File,
    status,
)
from fastapi.responses import StreamingResponse

from app.api.deps import get_client_ip, get_client_user_agent
from app.core.exceptions import ValidationError
from app.schemas.common import APIResponse
from app.schemas.verification import (
    PublicVerificationResponse,
    FileVerificationResponse,
)
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/public", tags=["Public Verification"])


@router.get(
    "/verify/{verification_code}",
    response_model=APIResponse[PublicVerificationResponse],
    summary="Publicly verify a certificate by verification code",
    description="No authentication required. Returns privacy-safe certificate verification details.",
)
async def public_verify_certificate(
    verification_code: str,
    request: Request,
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    result = await VerificationService.verify_by_code(
        code=verification_code,
        user_agent=ua,
        ip_address=ip,
    )
    return APIResponse.ok(result)


@router.post(
    "/verify-file",
    response_model=APIResponse[FileVerificationResponse],
    summary="Verify an uploaded certificate PDF file by cryptographic hash",
    description="Calculates SHA-256 of uploaded PDF and checks authentic matching certificate on platform.",
)
async def public_verify_certificate_file(
    request: Request,
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise ValidationError(message="Only PDF files are supported for file verification", code="INVALID_FILE_TYPE")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:  # 20MB limit
        raise ValidationError(message="File size exceeds maximum limit of 20MB", code="FILE_TOO_LARGE")

    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    result = await VerificationService.verify_by_file(
        file_bytes=content,
        user_agent=ua,
        ip_address=ip,
    )
    return APIResponse.ok(result)


@router.get(
    "/certificates/{verification_code}/download",
    summary="Public download of certificate PDF",
    description="Allows public certificate download if public download is enabled by the issuer.",
)
async def public_download_certificate(
    verification_code: str,
):
    pdf_bytes, filename = await VerificationService.get_public_pdf_bytes(verification_code)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
