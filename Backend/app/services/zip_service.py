from __future__ import annotations
import os
import re
import zipfile
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.issuance_job_repository import IssuanceJobRepository
from app.repositories.issuance_item_repository import IssuanceItemRepository
from app.repositories.certificate_repository import CertificateRepository
from app.services.storage_service import StorageService
from app.queue.redis import QueueManager
from app.queue.tasks import TASK_CREATE_ZIP
from app.schemas.issuance import ZipStatusResponse

logger = logging.getLogger(__name__)


def sanitize_filename(cert_number: str, recipient_name: str) -> str:
    """
    Sanitize recipient name and certificate number into a safe filename.
    Removes invalid Windows/Linux characters: / \\ : * ? \" < > | and path traversal sequences.
    """
    safe_number = re.sub(r'[\/\\:\*\?"<>\|\.\s]+', "-", cert_number.strip()).strip("-")
    safe_name = re.sub(r'[\/\\:\*\?"<>\|\.\s]+', "-", recipient_name.strip()).strip("-")
    
    if not safe_name:
        safe_name = "recipient"
    if not safe_number:
        safe_number = "certificate"
        
    return f"{safe_number}_{safe_name}.pdf"


class ZipService:
    @classmethod
    async def request_zip(cls, job_id: str, org_id: str, user_id: str) -> ZipStatusResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        zip_info = job.get("zip_info") or {}
        status = zip_info.get("status", "not_requested")

        # Check if already ready and not expired
        if status == "ready":
            expires_at = zip_info.get("expires_at")
            if isinstance(expires_at, str):
                try:
                    expires_at = datetime.fromisoformat(expires_at)
                except Exception:
                    expires_at = None
            if expires_at and expires_at > datetime.now(timezone.utc):
                return ZipStatusResponse(
                    job_id=job_id,
                    status="ready",
                    download_url=f"/api/v1/issuance-jobs/{job_id}/zip/download",
                    size_bytes=zip_info.get("size_bytes"),
                    created_at=zip_info.get("created_at"),
                    expires_at=expires_at,
                )

        # Mark as queued in job document
        queued_info = {
            "status": "queued",
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "storage_key": None,
            "size_bytes": None,
            "created_at": None,
            "expires_at": None,
            "error": None,
        }
        await IssuanceJobRepository.update_zip_info(job_id, queued_info)

        # Enqueue background task — P12.02: No web-server fallback in production
        queued = await QueueManager.enqueue(TASK_CREATE_ZIP, job_id, org_id)
        if not queued:
            if settings.APP_ENV == "test":
                import asyncio
                asyncio.create_task(cls.generate_zip(job_id, org_id))
            else:
                logger.error("Failed to enqueue ZIP creation for job %s: Redis queue is unavailable", job_id)
                from app.core.exceptions import AppException
                raise AppException(
                    code="QUEUE_UNAVAILABLE",
                    message="Background worker queue is currently unavailable for ZIP archive creation.",
                    status_code=503,
                )

        return ZipStatusResponse(
            job_id=job_id,
            status="queued",
            download_url=None,
        )

    @classmethod
    async def get_zip_status(cls, job_id: str, org_id: str) -> ZipStatusResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        zip_info = job.get("zip_info") or {}
        status = zip_info.get("status", "not_requested")

        # Check if expired
        expires_at = zip_info.get("expires_at")
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except Exception:
                expires_at = None

        if status == "ready" and expires_at and expires_at <= datetime.now(timezone.utc):
            status = "expired"
            zip_info["status"] = "expired"
            await IssuanceJobRepository.update_zip_info(job_id, zip_info)

        download_url = f"/api/v1/issuance-jobs/{job_id}/zip/download" if status == "ready" else None

        return ZipStatusResponse(
            job_id=job_id,
            status=status,
            download_url=download_url,
            size_bytes=zip_info.get("size_bytes"),
            created_at=zip_info.get("created_at"),
            expires_at=expires_at,
            error=zip_info.get("error"),
        )

    @classmethod
    async def generate_zip(cls, job_id: str, org_id: str) -> Dict[str, Any]:
        """
        Worker task: stream generated certificates into a zip archive.
        """
        logger.info("Starting ZIP generation for job_id=%s, org_id=%s", job_id, org_id)
        await IssuanceJobRepository.update_zip_info(job_id, {"status": "processing"})

        try:
            # 1. Fetch completed items with certificate_ids
            items, _ = await IssuanceItemRepository.list_items(job_id=job_id, status="completed", limit=10000)
            if not items:
                raise ValidationError(message="No completed certificates found for this job", code="NO_CERTIFICATES")

            # 2. Setup zip target path
            base_dir = Path(StorageService.get_base_dir()) / "zips" / org_id / job_id
            base_dir.mkdir(parents=True, exist_ok=True)
            zip_file_path = base_dir / "certificates.zip"
            zip_storage_key = str((Path("zips") / org_id / job_id / "certificates.zip").as_posix())

            # 3. Stream certificates into ZipFile
            with zipfile.ZipFile(zip_file_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
                seen_filenames = set()

                for item in items:
                    cert_id = item.get("certificate_id")
                    if not cert_id:
                        continue

                    cert_doc = await CertificateRepository.get_by_id(cert_id, org_id)
                    if not cert_doc:
                        continue

                    pdf_key = cert_doc.get("file", {}).get("pdf_key")
                    if not pdf_key:
                        continue

                    pdf_bytes = StorageService.read_file(pdf_key)
                    if not pdf_bytes:
                        continue

                    cert_number = cert_doc.get("certificate_number", "cert")
                    recip_name = cert_doc.get("recipient", {}).get("name", "recipient")
                    filename = sanitize_filename(cert_number, recip_name)

                    # Ensure unique filename in zip archive
                    unique_filename = filename
                    counter = 1
                    while unique_filename in seen_filenames:
                        unique_filename = f"{filename[:-4]}_{counter}.pdf"
                        counter += 1
                    seen_filenames.add(unique_filename)

                    archive.writestr(unique_filename, pdf_bytes)

            size_bytes = os.path.getsize(zip_file_path)
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(hours=settings.ZIP_EXPIRY_HOURS)

            ready_info = {
                "status": "ready",
                "storage_key": zip_storage_key,
                "size_bytes": size_bytes,
                "created_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "error": None,
            }
            await IssuanceJobRepository.update_zip_info(job_id, ready_info)
            logger.info("ZIP generation completed for job_id=%s, size=%d bytes", job_id, size_bytes)
            return ready_info

        except Exception as exc:
            logger.exception("ZIP generation failed for job_id=%s: %s", job_id, exc)
            error_info = {
                "status": "failed",
                "error": str(exc)[:500],
            }
            await IssuanceJobRepository.update_zip_info(job_id, error_info)
            raise
