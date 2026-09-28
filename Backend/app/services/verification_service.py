from __future__ import annotations
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError, AppException
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.verification_event_repository import VerificationEventRepository
from app.services.storage_service import StorageService
from app.services.rate_limiter import RateLimiter
from app.services.verification_cache import VerificationCache
from app.services.hash_service import HashService
from app.schemas.verification import (
    PublicVerificationResponse,
    PublicCertificateDetail,
    FileVerificationResponse,
    IntegrityCheckResponse,
    BulkRevokeResponse,
    CertificateTimelineResponse,
    CertificateTimelineItem,
)
from app.schemas.certificate import CertificateResponse

logger = logging.getLogger(__name__)


def _hash_ip(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


class VerificationService:
    @classmethod
    async def verify_by_code(
        cls,
        code: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> PublicVerificationResponse:
        """
        Public verification of a certificate by its code.
        Privacy-preserving, cached in Redis, rate-limited, and records verification event.
        """
        norm_code = code.upper().strip()

        # 1. Rate limiting check
        rate_key = f"verify_ip:{_hash_ip(ip_address) or 'unknown'}"
        is_allowed = await RateLimiter.is_allowed(
            rate_key,
            max_requests=settings.RATE_LIMIT_PUBLIC_VERIFY_PER_MINUTE,
            window_seconds=60,
        )
        if not is_allowed:
            raise AppException(
                code="RATE_LIMIT_EXCEEDED",
                message="Too many verification requests. Please try again in a moment.",
                status_code=429,
            )

        # 2. Check Redis cache
        cached = await VerificationCache.get(norm_code)
        if cached:
            # Still record verification event for analytics
            cert_id = cached.get("certificate_id")
            org_id = cached.get("organization_id")
            await VerificationEventRepository.create(
                certificate_id=cert_id,
                verification_code=norm_code,
                organization_id=org_id,
                result=cached.get("status", "valid"),
                user_agent=user_agent,
                ip_hash=_hash_ip(ip_address),
            )
            # Remove internal fields from response if any
            clean_cached = {k: v for k, v in cached.items() if k not in ("certificate_id", "organization_id")}
            return PublicVerificationResponse(**clean_cached)

        # 3. Lookup in MongoDB
        doc = await CertificateRepository.get_by_verification_code(norm_code)
        now = datetime.now(timezone.utc)

        if not doc:
            # Record failed scan event
            await VerificationEventRepository.create(
                certificate_id=None,
                verification_code=norm_code,
                organization_id=None,
                result="not_found",
                user_agent=user_agent,
                ip_hash=_hash_ip(ip_address),
            )
            return PublicVerificationResponse(
                valid=False,
                status="not_found",
                verified_at=now,
                message="Certificate not found. Please check the code and try again.",
            )

        cert_id = doc["id"]
        org_id = doc.get("organization_id")
        current_status = doc.get("status", "unknown")

        # 4. Check for revocation
        if current_status == "revoked":
            await VerificationEventRepository.create(
                certificate_id=cert_id,
                verification_code=norm_code,
                organization_id=org_id,
                result="revoked",
                user_agent=user_agent,
                ip_hash=_hash_ip(ip_address),
            )
            resp = PublicVerificationResponse(
                valid=False,
                status="revoked",
                certificate=PublicCertificateDetail(
                    certificate_number=doc.get("certificate_number", "Unknown"),
                    recipient_name=doc.get("recipient", {}).get("name", "Recipient"),
                    public_download_available=False,
                ),
                revoked_at=doc.get("revoked_at"),
                revocation_reason=doc.get("revocation_reason"),
                verified_at=now,
                message="This certificate was previously issued but has been revoked by the issuing organization.",
            )
            # Cache revoked status
            cache_payload = resp.model_dump()
            cache_payload["certificate_id"] = cert_id
            cache_payload["organization_id"] = org_id
            await VerificationCache.set(norm_code, cache_payload)
            return resp

        # 5. Check for expiration
        expires_at = doc.get("expires_at")
        if expires_at and expires_at <= now:
            await VerificationEventRepository.create(
                certificate_id=cert_id,
                verification_code=norm_code,
                organization_id=org_id,
                result="expired",
                user_agent=user_agent,
                ip_hash=_hash_ip(ip_address),
            )
            resp = PublicVerificationResponse(
                valid=False,
                status="expired",
                certificate=PublicCertificateDetail(
                    certificate_number=doc.get("certificate_number", "Unknown"),
                    recipient_name=doc.get("recipient", {}).get("name", "Recipient"),
                    public_download_available=False,
                ),
                expires_at=expires_at,
                verified_at=now,
                message="This certificate has expired.",
            )
            return resp

        # 6. Valid Certificate
        await VerificationEventRepository.create(
            certificate_id=cert_id,
            verification_code=norm_code,
            organization_id=org_id,
            result="valid",
            user_agent=user_agent,
            ip_hash=_hash_ip(ip_address),
        )

        # Fetch organization display name
        org_doc = await OrganizationRepository.get_by_id(str(org_id)) if org_id else None
        issuer_name = org_doc.get("name") if org_doc else getattr(settings, "APP_NAME", "CertiFlow")

        # Format issue date
        issued_dt = doc.get("issued_at") or doc.get("created_at")
        issue_date_str = issued_dt.strftime("%d %B %Y") if isinstance(issued_dt, datetime) else str(issued_dt or "")

        program_name = (
            doc.get("data", {}).get("program_name")
            or doc.get("data", {}).get("course")
            or doc.get("template_snapshot", {}).get("template_name")
            or "Certificate Program"
        )

        detail = PublicCertificateDetail(
            certificate_number=doc.get("certificate_number", ""),
            recipient_name=doc.get("recipient", {}).get("name", ""),
            program_name=program_name,
            issue_date=issue_date_str,
            issuer_name=issuer_name,
            public_download_available=settings.PUBLIC_DOWNLOAD_ENABLED,
        )

        resp = PublicVerificationResponse(
            valid=True,
            status="valid",
            certificate=detail,
            verified_at=now,
            message="Certificate is authentic and valid.",
        )

        # Cache response
        cache_payload = resp.model_dump()
        cache_payload["certificate_id"] = cert_id
        cache_payload["organization_id"] = org_id
        await VerificationCache.set(norm_code, cache_payload)

        return resp

    @classmethod
    async def verify_by_file(
        cls,
        file_bytes: bytes,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> FileVerificationResponse:
        """
        Public verification by uploading the original PDF.
        Calculates SHA-256 and searches for an authentic matching record.
        """
        file_sha256 = HashService.sha256(file_bytes)
        doc = await CertificateRepository.get_by_sha256(file_sha256)

        if not doc:
            return FileVerificationResponse(
                valid=False,
                status="invalid",
                integrity_matched=False,
                file_sha256=file_sha256,
                message="File integrity check failed. The uploaded file does not match any certificate issued on our platform or has been altered.",
            )

        status = doc.get("status", "unknown")
        is_valid = (status == "generated")

        org_doc = await OrganizationRepository.get_by_id(str(doc.get("organization_id"))) if doc.get("organization_id") else None
        issuer_name = org_doc.get("name") if org_doc else getattr(settings, "APP_NAME", "CertiFlow")

        issued_dt = doc.get("issued_at") or doc.get("created_at")
        issue_date_str = issued_dt.strftime("%d %B %Y") if isinstance(issued_dt, datetime) else str(issued_dt or "")

        detail = PublicCertificateDetail(
            certificate_number=doc.get("certificate_number", ""),
            recipient_name=doc.get("recipient", {}).get("name", ""),
            program_name=doc.get("template_snapshot", {}).get("template_name", "Certificate Program"),
            issue_date=issue_date_str,
            issuer_name=issuer_name,
            public_download_available=settings.PUBLIC_DOWNLOAD_ENABLED,
        )

        return FileVerificationResponse(
            valid=is_valid,
            status=status,
            integrity_matched=True,
            file_sha256=file_sha256,
            certificate=detail,
            message="SHA-256 integrity check verified. File matches the authentic issued certificate.",
        )

    @classmethod
    async def check_integrity(cls, cert_id: str, org_id: str) -> IntegrityCheckResponse:
        """
        Internal integrity check: compares physical stored PDF SHA-256 against database record.
        """
        doc = await CertificateRepository.get_by_id(cert_id, org_id)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        pdf_key = doc.get("file", {}).get("pdf_key")
        stored_hash = doc.get("file", {}).get("sha256")

        if not pdf_key:
            raise NotFoundError(message="Certificate file key not found", code="PDF_NOT_FOUND")

        pdf_bytes = StorageService.read_file(pdf_key)
        if not pdf_bytes:
            raise NotFoundError(message="Physical certificate file not found on storage", code="FILE_NOT_FOUND")

        current_hash = HashService.sha256(pdf_bytes)
        matched = (stored_hash == current_hash)

        return IntegrityCheckResponse(
            certificate_id=cert_id,
            certificate_number=doc.get("certificate_number", ""),
            valid=matched,
            algorithm="SHA-256",
            stored_hash=stored_hash,
            current_hash=current_hash,
            matched=matched,
            checked_at=datetime.now(timezone.utc),
        )

    @classmethod
    async def revoke_certificate(
        cls,
        cert_id: str,
        org_id: str,
        user_id: str,
        reason: str,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> CertificateResponse:
        doc = await CertificateRepository.get_by_id(cert_id, org_id)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        if doc.get("status") == "revoked":
            raise ValidationError(message="Certificate is already revoked", code="ALREADY_REVOKED")

        updated = await CertificateRepository.revoke(
            cert_id=cert_id,
            organization_id=org_id,
            reason=reason,
            revoked_by=user_id,
            notes=notes,
        )

        # Invalidate verification cache
        verif_code = doc.get("verification_code")
        if verif_code:
            await VerificationCache.invalidate(verif_code)

        # Audit log
        await AuditLogRepository.log_event(
            action="certificate.revoked",
            resource_type="certificate",
            resource_id=cert_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"reason": reason, "notes": notes or ""},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        try:
            from app.services.webhook_service import WebhookService
            await WebhookService.dispatch_event(
                org_id=org_id,
                event_type="certificate.revoked",
                data={
                    "certificate_id": cert_id,
                    "certificate_number": doc.get("certificate_number"),
                    "reason": reason,
                },
            )
        except Exception:
            pass

        return CertificateResponse(**updated)

    @classmethod
    async def restore_certificate(
        cls,
        cert_id: str,
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> CertificateResponse:
        doc = await CertificateRepository.get_by_id(cert_id, org_id)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        if doc.get("status") != "revoked":
            raise ValidationError(
                message=f"Cannot restore certificate with status '{doc.get('status')}' (must be 'revoked')",
                code="NOT_REVOKED",
            )

        updated = await CertificateRepository.restore(
            cert_id=cert_id,
            organization_id=org_id,
            restored_by=user_id,
        )

        # Invalidate verification cache
        verif_code = doc.get("verification_code")
        if verif_code:
            await VerificationCache.invalidate(verif_code)

        # Audit log
        await AuditLogRepository.log_event(
            action="certificate.restored",
            resource_type="certificate",
            resource_id=cert_id,
            organization_id=org_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        try:
            from app.services.webhook_service import WebhookService
            await WebhookService.dispatch_event(
                org_id=org_id,
                event_type="certificate.restored",
                data={
                    "certificate_id": cert_id,
                    "certificate_number": doc.get("certificate_number"),
                },
            )
        except Exception:
            pass

        return CertificateResponse(**updated)

    @classmethod
    async def bulk_revoke(
        cls,
        cert_ids: List[str],
        org_id: str,
        user_id: str,
        reason: str,
        notes: Optional[str] = None,
    ) -> BulkRevokeResponse:
        revoked_count, failed_ids = await CertificateRepository.bulk_revoke(
            cert_ids=cert_ids,
            organization_id=org_id,
            reason=reason,
            revoked_by=user_id,
            notes=notes,
        )

        # Invalidate caches
        for cid in cert_ids:
            doc = await CertificateRepository.get_by_id(cid, org_id)
            if doc and doc.get("verification_code"):
                await VerificationCache.invalidate(doc["verification_code"])

        # Audit log
        await AuditLogRepository.log_event(
            action="certificate.bulk_revoked",
            resource_type="certificate",
            resource_id="bulk",
            organization_id=org_id,
            user_id=user_id,
            metadata={"revoked_count": revoked_count, "reason": reason},
        )

        return BulkRevokeResponse(
            revoked_count=revoked_count,
            failed_ids=failed_ids,
            message=f"Successfully revoked {revoked_count} certificate(s).",
        )

    @classmethod
    async def get_certificate_timeline(cls, cert_id: str, org_id: str) -> CertificateTimelineResponse:
        doc = await CertificateRepository.get_by_id(cert_id, org_id)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        events: List[CertificateTimelineItem] = []

        # 1. Issued/Generated event
        if doc.get("issued_at") or doc.get("created_at"):
            events.append(CertificateTimelineItem(
                type="generated",
                title="Certificate Generated & Issued",
                timestamp=doc.get("issued_at") or doc.get("created_at"),
                metadata={"certificate_number": doc.get("certificate_number")},
            ))

        # 2. Verification scan events
        scans = await VerificationEventRepository.list_by_certificate(cert_id, limit=50)
        for s in scans:
            events.append(CertificateTimelineItem(
                type=f"verified_{s.get('result')}",
                title=f"Verification Scan ({s.get('result', '').upper()})",
                timestamp=s.get("timestamp"),
                metadata={"user_agent": s.get("user_agent")},
            ))

        # 3. Revoked / Restored
        if doc.get("revoked_at"):
            events.append(CertificateTimelineItem(
                type="revoked",
                title="Certificate Revoked",
                timestamp=doc["revoked_at"],
                metadata={"reason": doc.get("revocation_reason")},
            ))

        if doc.get("restored_at"):
            events.append(CertificateTimelineItem(
                type="restored",
                title="Certificate Restored",
                timestamp=doc["restored_at"],
            ))

        # Sort chronological
        events.sort(key=lambda e: e.timestamp)

        return CertificateTimelineResponse(
            certificate_id=cert_id,
            certificate_number=doc.get("certificate_number", ""),
            events=events,
        )

    @classmethod
    async def get_public_pdf_bytes(cls, verification_code: str, token: Optional[str] = None) -> tuple[bytes, str]:
        from app.services.signed_url_service import SignedURLService

        if token:
            if not SignedURLService.verify_token(verification_code, token):
                raise ForbiddenError(message="Invalid or expired download link", code="INVALID_SIGNED_URL")
        elif not settings.PUBLIC_DOWNLOAD_ENABLED:
            raise ForbiddenError(message="Public download of certificates is disabled", code="PUBLIC_DOWNLOAD_DISABLED")

        clean_code = verification_code.upper().strip()
        doc = await CertificateRepository.get_by_verification_code(clean_code)
        if not doc:
            # Fallback check by certificate ID if an ID was passed in URL
            doc = await CertificateRepository.get_by_id(verification_code)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        if doc.get("status") == "revoked":
            raise ValidationError(message="Cannot download a revoked certificate", code="CERTIFICATE_REVOKED")

        pdf_key = doc.get("file", {}).get("pdf_key") or doc.get("storage_key") or doc.get("pdf_storage_key")
        if not pdf_key:
            raise NotFoundError(message="Certificate file not found", code="PDF_NOT_FOUND")

        pdf_bytes = StorageService.read_file(pdf_key)
        if not pdf_bytes:
            raise NotFoundError(message="Certificate file not found on storage", code="PDF_NOT_FOUND")

        cert_number = doc.get("certificate_number", "certificate")
        return pdf_bytes, f"{cert_number}.pdf"
