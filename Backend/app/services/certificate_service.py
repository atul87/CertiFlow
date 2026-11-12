"""
CertificateService — P3.01 / P3.37 / P3.44–P3.48 / P3.57–P3.59 / P3.64

Implements the full certificate generation pipeline:

  PREVIEW mode (no persistent record):
    validate → resolve data → render → return base64 PNG

  GENERATE mode (official issuance):
    validate → resolve data → generate ID + verification code →
    render → PDF → SHA-256 → store files → save MongoDB record →
    audit log → return certificate response
"""
from __future__ import annotations
import io
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError, AppException
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.template_version_repository import TemplateVersionRepository
from app.services.certificate_id_service import CertificateIDService
from app.services.hash_service import HashService
from app.services.placeholder_service import PlaceholderService
from app.services.storage_service import StorageService
from app.services.rendering.renderer import render_certificate
from app.services.rendering.pdf_renderer import render_pdf
from app.schemas.certificate import (
    CertificatePreviewRequest,
    CertificateGenerateRequest,
    CertificateResponse,
    CertificatePreviewResponse,
)

logger = logging.getLogger(__name__)

# Error codes — P3.53
class RenderError(AppException):
    def __init__(self, code: str, message: str, details: Any = None):
        super().__init__(code=code, message=message, status_code=422, details=details)


async def prefetch_template_assets(version_doc: dict, org_id: str) -> dict[str, bytes]:
    """Prefetch all assets referenced in version_doc asynchronously in the current event loop.
    
    Eliminates thread-pool asyncio.run() calls during rendering — P12.01.
    """
    asset_ids = set()
    bg_asset_id = version_doc.get("background_asset_id")
    if bg_asset_id:
        asset_ids.add(str(bg_asset_id))
    for layer in version_doc.get("canvas", {}).get("layers", []):
        for key in ("asset_id", "signature_id", "image_asset_id", "logo_id"):
            val = layer.get(key)
            if val:
                asset_ids.add(str(val))

    cache: dict[str, bytes] = {}
    for aid in asset_ids:
        try:
            asset = await AssetRepository.get_by_id(aid)
            if asset and asset.get("storage_key"):
                b = StorageService.read_file(asset["storage_key"])
                if b:
                    cache[aid] = b
        except Exception as exc:
            logger.warning("Could not prefetch asset %s: %s", aid, exc)
    return cache


def _make_asset_loader(org_id: str, preloaded_assets: Optional[dict[str, bytes]] = None):
    """Return a purely synchronous callable that loads asset bytes from cache or storage.
    
    Eliminates asyncio.run() and thread-pool DB access to prevent event-loop conflicts.
    """
    cache = dict(preloaded_assets or {})

    def loader(asset_id: str) -> Optional[bytes]:
        if not asset_id:
            return None
        str_id = str(asset_id)
        if str_id in cache:
            return cache[str_id]
        # Direct storage read fallback if asset_id is a storage key or path
        try:
            data = StorageService.read_file(str_id)
            if data:
                cache[str_id] = data
                return data
        except Exception:
            pass
        return None

    return loader


def _build_system_variables(
    certificate_number: str,
    verification_code: str,
    org_name: str,
    template_name: str,
    issued_at: datetime,
) -> dict[str, str]:
    """Build all system-injected template variables — P3.08."""
    base_url = getattr(settings, "APP_BASE_URL", "https://certiflow.io")
    verification_url = CertificateIDService.generate_verification_url(
        base_url, verification_code
    )
    return {
        "certificate_id": certificate_number,
        "certificate_number": certificate_number,
        "verification_code": verification_code,
        "verification_url": verification_url,
        "issued_at": issued_at.strftime("%d %B %Y"),
        "issue_date": issued_at.strftime("%d %B %Y"),
        "organization_name": org_name,
        "template_name": template_name,
    }


def _validate_required_fields(
    template_fields: list[dict],
    resolved_data: dict[str, Any],
) -> None:
    """
    Ensure every required recipient field has a non-empty value — P3.10.
    Raises ValidationError with MISSING_REQUIRED_FIELD if anything is absent.
    """
    for field in template_fields:
        key = field.get("key", "")
        required = field.get("required", True)
        source = field.get("source", "recipient")
        if source == "system":
            continue  # injected automatically
        if required and not resolved_data.get(key):
            raise ValidationError(
                message=f"Required field '{field.get('label', key)}' is missing or empty",
                code="MISSING_REQUIRED_FIELD",
                details={"field": key},
            )


def _save_certificate_files(
    org_id: str,
    cert_id: str,
    pdf_bytes: bytes,
    preview_bytes: bytes,
) -> tuple[str, str]:
    """
    Persist PDF and preview PNG to disk storage — P3.43.
    Returns (pdf_key, preview_key).
    """
    year = datetime.now(timezone.utc).year
    prefix = Path("certificates") / org_id / str(year) / cert_id
    pdf_key = StorageService.save_bytes(
        pdf_bytes, (prefix / "certificate.pdf").as_posix(), "application/pdf"
    )
    preview_key = StorageService.save_bytes(
        preview_bytes, (prefix / "preview.png").as_posix(), "image/png"
    )
    return pdf_key, preview_key


class CertificateService:

    # ------------------------------------------------------------------
    # PREVIEW (no persistent record)
    # ------------------------------------------------------------------

    @classmethod
    async def preview(
        cls,
        request: CertificatePreviewRequest,
        org_id: str,
        user_id: str,
    ) -> CertificatePreviewResponse:
        """
        Render a certificate preview without creating an official record.
        Returns base64 PNG data URL — P3.45 / P3.46.
        """
        import base64

        t0 = time.monotonic()

        # 1. Load and validate template version
        version_doc = await TemplateVersionRepository.get_by_id(
            str(request.template_version_id), org_id
        )
        if not version_doc:
            raise NotFoundError(
                message="Template version not found",
                code="TEMPLATE_VERSION_NOT_FOUND",
            )
        if version_doc.get("status") != "published":
            raise ValidationError(
                message="Only published template versions can generate certificates",
                code="TEMPLATE_NOT_PUBLISHED",
            )

        # 2. Build resolved data (recipient data + system variables)
        dummy_cert_number = "CERT-PREVIEW-000000"
        dummy_verification_code = "PREVIEW_CODE"
        issued_at = datetime.now(timezone.utc)

        template_doc = await TemplateRepository.get_by_id(
            str(version_doc.get("template_id", "")), org_id
        )
        org_name = getattr(settings, "APP_NAME", "CertiFlow")
        template_name = template_doc.get("name", "Certificate") if template_doc else "Certificate"

        system_vars = _build_system_variables(
            dummy_cert_number, dummy_verification_code, org_name, template_name, issued_at
        )

        recipient_data = dict(request.data or {})
        resolved_data: dict[str, Any] = {**recipient_data, **system_vars}

        # 3. Validate required fields
        template_fields = version_doc.get("fields", [])
        _validate_required_fields(template_fields, resolved_data)

        # 4. Load background asset and prefetch all template assets asynchronously
        preloaded_assets = await prefetch_template_assets(version_doc, org_id)
        bg_asset_id = version_doc.get("background_asset_id")
        bg_bytes: Optional[bytes] = preloaded_assets.get(str(bg_asset_id)) if bg_asset_id else None

        # 5. Render canvas
        asset_loader = _make_asset_loader(org_id, preloaded_assets)
        render_result = render_certificate(
            version_doc=version_doc,
            resolved_data=resolved_data,
            asset_loader=asset_loader,
            bg_image_bytes=bg_bytes,
        )

        # 6. Build response
        preview_b64 = "data:image/png;base64," + base64.b64encode(
            render_result["preview_bytes"]
        ).decode()

        total_ms = round((time.monotonic() - t0) * 1000, 1)

        # Audit preview event
        await AuditLogRepository.log_event(
            action="certificate.previewed",
            resource_type="template_version",
            resource_id=str(request.template_version_id),
            organization_id=org_id,
            user_id=user_id,
            metadata={"template_version_id": str(request.template_version_id)},
        )

        return CertificatePreviewResponse(
            preview_url=preview_b64,
            overflows=render_result["overflows"],
            render_time_ms=total_ms,
            diagnostics=render_result["diagnostics"],
        )

    # ------------------------------------------------------------------
    # GENERATE (official issuance)
    # ------------------------------------------------------------------

    @classmethod
    async def generate(
        cls,
        request: CertificateGenerateRequest,
        org_id: str,
        user_id: str,
        idempotency_key: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        preloaded_assets: Optional[dict[str, bytes]] = None,
    ) -> CertificateResponse:
        """
        Full official certificate generation pipeline — P3.47.
        """
        t0 = time.monotonic()

        # Idempotency check — P3.48 & P12.18
        if not idempotency_key and request.import_id and request.import_row_id:
            idempotency_key = f"imp_{request.import_id}_row_{request.import_row_id}"

        existing = None
        if idempotency_key:
            existing = await CertificateRepository.get_by_idempotency_key(
                idempotency_key, org_id
            )
        if not existing and request.import_id and request.import_row_id:
            existing = await CertificateRepository.get_by_import_row(
                org_id, str(request.import_id), str(request.import_row_id)
            )

        if existing and existing.get("status") in ("generated", "generating", "issued"):
            logger.info("Idempotency hit for key=%s (cert_id=%s)", idempotency_key, existing.get("id"))
            return CertificateResponse(**existing)

        # Quota check — P10
        from app.services.quota_service import QuotaService
        await QuotaService.check_certificate_quota(org_id=org_id, quantity=1)

        # 1. Load template version (must be published)
        version_doc = await TemplateVersionRepository.get_by_id(
            str(request.template_version_id), org_id
        )
        if not version_doc:
            raise NotFoundError(
                message="Template version not found",
                code="TEMPLATE_VERSION_NOT_FOUND",
            )
        if version_doc.get("status") != "published":
            raise ValidationError(
                message="Only published template versions can generate certificates",
                code="TEMPLATE_NOT_PUBLISHED",
            )

        template_id = str(version_doc.get("template_id", ""))
        template_doc = await TemplateRepository.get_by_id(template_id, org_id)
        org_name = getattr(settings, "APP_NAME", "CertiFlow")
        template_name = template_doc.get("name", "Certificate") if template_doc else "Certificate"

        # 2. Generate identifiers — P3.04 / P3.05
        certificate_number = await CertificateIDService.generate_certificate_number(
            organization_id=org_id
        )
        verification_code = CertificateIDService.generate_verification_code()
        issued_at = datetime.now(timezone.utc)

        # 3. Build system variables — P3.08
        system_vars = _build_system_variables(
            certificate_number, verification_code, org_name, template_name, issued_at
        )

        recipient_input = dict(request.data or {})

        # Normalize common aliases so both uppercase tags ({{NAME}}) and snake_case fields work
        if "NAME" in recipient_input and "recipient_name" not in recipient_input:
            recipient_input["recipient_name"] = recipient_input["NAME"]
        elif "recipient_name" in recipient_input and "NAME" not in recipient_input:
            recipient_input["NAME"] = recipient_input["recipient_name"]

        if "COURSE" in recipient_input and "program_name" not in recipient_input:
            recipient_input["program_name"] = recipient_input["COURSE"]
        elif "program_name" in recipient_input and "COURSE" not in recipient_input:
            recipient_input["COURSE"] = recipient_input["program_name"]

        if "EMAIL" in recipient_input and "recipient_email" not in recipient_input:
            recipient_input["recipient_email"] = recipient_input["EMAIL"]
        elif "recipient_email" in recipient_input and "EMAIL" not in recipient_input:
            recipient_input["EMAIL"] = recipient_input["recipient_email"]

        resolved_data: dict[str, Any] = {**recipient_input, **system_vars}

        # 4. Validate required fields — P3.10
        template_fields = version_doc.get("fields", [])
        _validate_required_fields(template_fields, resolved_data)

        # 5. Build recipient + data snapshots — P3.57–P3.59
        recipient_snapshot = {
            "name": resolved_data.get("recipient_name", ""),
            "email": resolved_data.get("recipient_email", ""),
        }
        data_snapshot = dict(recipient_input)

        # 6. Template snapshot (version ID + version number for reproducibility)
        template_snapshot = {
            "template_id": template_id,
            "template_version_id": str(request.template_version_id),
            "version": version_doc.get("version", 1),
            "template_name": template_name,
        }

        # 7. Create certificate record in MongoDB (status=generating)
        cert_doc = await CertificateRepository.create(
            organization_id=org_id,
            template_id=template_id,
            template_version_id=str(request.template_version_id),
            certificate_number=certificate_number,
            verification_code=verification_code,
            recipient=recipient_snapshot,
            data=data_snapshot,
            template_snapshot=template_snapshot,
            created_by=user_id,
            import_id=str(request.import_id) if request.import_id else None,
            import_row_id=str(request.import_row_id) if request.import_row_id else None,
            idempotency_key=idempotency_key,
        )
        cert_id = cert_doc["id"]

        try:
            # 8. Load background asset & prefetch template assets asynchronously
            if preloaded_assets is None:
                preloaded_assets = await prefetch_template_assets(version_doc, org_id)

            bg_asset_id = version_doc.get("background_asset_id")
            bg_bytes: Optional[bytes] = preloaded_assets.get(str(bg_asset_id)) if bg_asset_id else None

            # 9. Render canvas — P3.14–P3.35 (pure synchronous execution, no asyncio.run)
            asset_loader = _make_asset_loader(org_id, preloaded_assets)
            render_result = render_certificate(
                version_doc=version_doc,
                resolved_data=resolved_data,
                asset_loader=asset_loader,
                bg_image_bytes=bg_bytes,
            )

            t_render = time.monotonic()

            # 10. Generate PDF — P3.36–P3.39
            pdf_bytes = render_pdf(
                canvas_image=render_result["canvas"],
                title=f"Certificate of Completion - {recipient_snapshot['name']}",
                author=org_name,
                subject=f"{template_name} Certificate",
                creator="CertiFlow Certificate Platform",
            )
            t_pdf = time.monotonic()

            # 11. SHA-256 — P3.41 / P3.42
            pdf_sha256 = HashService.sha256(pdf_bytes)

            # 12. Store files — P3.43
            pdf_key, preview_key = _save_certificate_files(
                org_id=org_id,
                cert_id=cert_id,
                pdf_bytes=pdf_bytes,
                preview_bytes=render_result["preview_bytes"],
            )

            t_store = time.monotonic()

            # 13. Build diagnostics — P3.55
            diagnostics = render_result["diagnostics"]
            diagnostics.update({
                "pdf_generation_time_ms": round((t_pdf - t_render) * 1000, 1),
                "storage_time_ms": round((t_store - t_pdf) * 1000, 1),
                "total_time_ms": round((t_store - t0) * 1000, 1),
            })

            # 14. Update MongoDB record to generated
            file_info = {
                "pdf_key": pdf_key,
                "preview_key": preview_key,
                "pdf_size": len(pdf_bytes),
                "preview_size": len(render_result["preview_bytes"]),
                "sha256": pdf_sha256,
            }
            updated = await CertificateRepository.update_status(
                cert_id=cert_id,
                status="generated",
                file_info=file_info,
                render_diagnostics=diagnostics,
            )

        except Exception as exc:
            # 15. Mark as failed — P3.52
            error_info = {
                "code": getattr(exc, "code", "RENDER_ERROR"),
                "message": str(exc)[:500],  # never expose full traceback
            }
            await CertificateRepository.update_status(
                cert_id=cert_id,
                status="failed",
                error=error_info,
            )
            logger.exception("Certificate generation failed for cert_id=%s", cert_id)
            raise RenderError(
                code=error_info["code"],
                message=f"Certificate generation failed: {error_info['message']}",
            ) from exc

        # 16. Audit log — P3.64
        await AuditLogRepository.log_event(
            action="certificate.generated",
            resource_type="certificate",
            resource_id=cert_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={
                "certificate_number": certificate_number,
                "template_version_id": str(request.template_version_id),
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # 17. Outbound webhook dispatch — P8
        try:
            from app.services.webhook_service import WebhookService
            await WebhookService.dispatch_event(
                org_id=org_id,
                event_type="certificate.generated",
                data={
                    "certificate_id": cert_id,
                    "certificate_number": certificate_number,
                    "verification_code": verification_code,
                    "recipient_email": recipient_snapshot.get("email"),
                    "recipient_name": recipient_snapshot.get("name"),
                },
            )
        except Exception as e:
            logger.warning("Failed to dispatch certificate.generated webhook: %s", e)

        # 18. Usage Metering — P10
        try:
            from app.services.usage_service import UsageService
            await UsageService.record_usage(
                org_id=org_id,
                metric="certificates_generated",
                quantity=1,
                resource_id=cert_id,
                source="certificate_service.generate",
            )
            total_bytes = len(pdf_bytes) + len(render_result["preview_bytes"])
            if total_bytes > 0:
                await UsageService.record_usage(
                    org_id=org_id,
                    metric="storage_bytes",
                    quantity=total_bytes,
                    resource_id=cert_id,
                    source="certificate_storage",
                )
        except Exception as e:
            logger.warning("Failed to record usage for cert %s: %s", cert_id, e)

        return CertificateResponse(**updated)

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    @classmethod
    async def get_certificate(cls, cert_id: str, org_id: str) -> CertificateResponse:
        doc = await CertificateRepository.get_by_id(cert_id, org_id)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")
        return CertificateResponse(**doc)

    @classmethod
    async def list_certificates(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        recipient_email: Optional[str] = None,
        search: Optional[str] = None,
        program: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        verification_code: Optional[str] = None,
    ) -> dict[str, Any]:
        items, total = await CertificateRepository.list_certificates(
            organization_id=org_id,
            page=page,
            limit=limit,
            status=status,
            template_id=template_id,
            recipient_email=recipient_email,
            search=search,
            program=program,
            from_date=from_date,
            to_date=to_date,
            verification_code=verification_code,
        )
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        return {
            "items": [CertificateResponse(**c) for c in items],
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        }

    @classmethod
    async def get_pdf_bytes(cls, cert_id: str, org_id: str) -> tuple[bytes, str]:
        """Return (pdf_bytes, filename) for secure download — P3.62."""
        doc = await CertificateRepository.get_by_id(cert_id, org_id)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")
        if doc.get("status") != "generated":
            raise ValidationError(
                message="Certificate is not yet generated or has been revoked",
                code="CERTIFICATE_NOT_AVAILABLE",
            )
        pdf_key = doc.get("file", {}).get("pdf_key")
        if not pdf_key:
            raise NotFoundError(message="Certificate PDF not found", code="PDF_NOT_FOUND")
        pdf_bytes = StorageService.read_file(pdf_key)
        if not pdf_bytes:
            raise NotFoundError(message="Certificate file not found on storage", code="PDF_NOT_FOUND")
        cert_number = doc.get("certificate_number", cert_id)
        return pdf_bytes, f"{cert_number}.pdf"

    @classmethod
    async def get_preview_bytes(cls, cert_id: str, org_id: str) -> bytes:
        """Return preview PNG bytes for the certificate — P3.38."""
        doc = await CertificateRepository.get_by_id(cert_id, org_id)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")
        preview_key = doc.get("file", {}).get("preview_key")
        if not preview_key:
            raise NotFoundError(message="Preview not found", code="PREVIEW_NOT_FOUND")
        preview_bytes = StorageService.read_file(preview_key)
        if not preview_bytes:
            raise NotFoundError(message="Preview file not found on storage", code="PREVIEW_NOT_FOUND")
        return preview_bytes

    @classmethod
    async def revoke_certificate(
        cls,
        cert_id: str,
        org_id: str,
        user_id: str,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> CertificateResponse:
        doc = await CertificateRepository.revoke(cert_id, org_id, reason=reason)
        if not doc:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        # Synchronize digital credential revocation — P11
        try:
            from app.services.credential_status_service import CredentialStatusService
            await CredentialStatusService.sync_revocation(
                organization_id=org_id,
                certificate_id=cert_id,
                reason=reason or "Certificate revoked by authority",
                actor_id=user_id,
            )
        except Exception as e:
            logger.warning("Failed to sync credential revocation for certificate %s: %s", cert_id, e)

        await AuditLogRepository.log_event(
            action="certificate.revoked",
            resource_type="certificate",
            resource_id=cert_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"reason": reason or ""},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return CertificateResponse(**doc)
