from __future__ import annotations
import asyncio
import logging
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.email_job_repository import EmailJobRepository
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.queue.redis import QueueManager
from app.queue.tasks import TASK_PROCESS_BULK_EMAIL_JOB
from app.workers.email_worker import process_bulk_email_job_task

logger = logging.getLogger(__name__)


class EmailJobService:

    @classmethod
    async def create_email_job(
        cls,
        org_id: str,
        certificate_ids: List[str],
        template_id: Optional[str],
        delivery_mode: str,
        user_id: str,
    ) -> Dict[str, Any]:
        if not certificate_ids:
            raise ValidationError(message="No certificate IDs provided", code="EMPTY_CERTIFICATE_LIST")

        # 1. Fetch certificates and verify ownership
        valid_certs = []
        for cid in certificate_ids:
            cert = await CertificateRepository.get_by_id(cid, org_id)
            if cert and cert.get("status") != "revoked":
                valid_certs.append(cert)

        if not valid_certs:
            raise ValidationError(
                message="No valid or active certificates found for the provided IDs",
                code="NO_VALID_CERTIFICATES",
            )

        # 2. Create EmailJob record
        job_doc = await EmailJobRepository.create(
            organization_id=org_id,
            total=len(valid_certs),
            template_id=template_id,
            delivery_mode=delivery_mode,
            created_by=user_id,
        )
        job_id = job_doc["id"]

        # 3. Create delivery records for each certificate
        for cert in valid_certs:
            recipient = cert.get("recipient", {})
            recipient_email = recipient.get("email") or ""
            recipient_name = recipient.get("name") or "Recipient"
            if not recipient_email:
                continue

            await EmailDeliveryRepository.create(
                organization_id=org_id,
                certificate_id=cert["id"],
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                template_id=template_id,
                delivery_mode=delivery_mode,
                issuance_job_id=cert.get("issuance_job_id"),
                email_job_id=job_id,
            )

        # 4. Audit log
        await AuditLogRepository.log_event(
            action="email_job.created",
            resource_type="email_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={
                "total": len(valid_certs),
                "template_id": template_id,
                "delivery_mode": delivery_mode,
            },
        )

        # 5. Enqueue ARQ task or run asynchronously
        queued = await QueueManager.enqueue(TASK_PROCESS_BULK_EMAIL_JOB, job_id, org_id)
        if not queued and settings.APP_ENV != "test":
            logger.info(f"Redis queue unavailable; executing bulk email job {job_id} via asyncio task")
            asyncio.create_task(process_bulk_email_job_task(None, job_id, org_id))

        return job_doc

    @classmethod
    async def get_job(cls, job_id: str, org_id: str) -> Dict[str, Any]:
        job = await EmailJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Email job not found", code="JOB_NOT_FOUND")
        return job

    @classmethod
    async def list_jobs(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await EmailJobRepository.list_jobs(org_id, page, limit)

    @classmethod
    async def pause_job(cls, job_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        job = await cls.get_job(job_id, org_id)
        if job["status"] not in ("queued", "processing", "starting"):
            raise ValidationError(message=f"Cannot pause job in status {job['status']}", code="INVALID_STATUS")

        updated = await EmailJobRepository.update_status(job_id, "paused")
        await AuditLogRepository.log_event(
            action="email_job.paused",
            resource_type="email_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
        )
        return updated or job

    @classmethod
    async def resume_job(cls, job_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        job = await cls.get_job(job_id, org_id)
        if job["status"] != "paused":
            raise ValidationError(message=f"Cannot resume job in status {job['status']}", code="INVALID_STATUS")

        updated = await EmailJobRepository.update_status(job_id, "processing")
        await AuditLogRepository.log_event(
            action="email_job.resumed",
            resource_type="email_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
        )

        # Trigger processing again
        queued = await QueueManager.enqueue(TASK_PROCESS_BULK_EMAIL_JOB, job_id, org_id)
        if not queued and settings.APP_ENV != "test":
            asyncio.create_task(process_bulk_email_job_task(None, job_id, org_id))

        return updated or job

    @classmethod
    async def cancel_job(cls, job_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        job = await cls.get_job(job_id, org_id)
        if job["status"] in ("completed", "completed_with_errors", "cancelled"):
            raise ValidationError(message=f"Cannot cancel job in status {job['status']}", code="INVALID_STATUS")

        updated = await EmailJobRepository.update_status(job_id, "cancelled")
        await AuditLogRepository.log_event(
            action="email_job.cancelled",
            resource_type="email_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
        )
        return updated or job
