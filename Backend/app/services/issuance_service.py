from __future__ import annotations
import csv
import io
import logging
from typing import Optional, Dict, Any, List, Tuple

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.import_repository import ImportRepository
from app.repositories.import_row_repository import ImportRowRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.template_version_repository import TemplateVersionRepository
from app.repositories.issuance_job_repository import IssuanceJobRepository
from app.repositories.issuance_item_repository import IssuanceItemRepository
from app.services.error_classifier import ErrorClassifier
from app.queue.redis import QueueManager
from app.queue.tasks import TASK_GENERATE_BULK_CERTIFICATES
from app.schemas.issuance import (
    IssuanceJobCreateRequest,
    IssuanceJobResponse,
    IssuanceItemResponse,
    IssuanceItemListResponse,
    IssuanceJobListResponse,
    ErrorRowItem,
)

logger = logging.getLogger(__name__)


class IssuanceService:
    @classmethod
    async def create_job(
        cls,
        request: IssuanceJobCreateRequest,
        org_id: str,
        user_id: str,
    ) -> IssuanceJobResponse:
        """
        Validate prerequisites, create parent issuance job, create items, and queue the task.
        """
        # 1. Validate template version
        version_doc = await TemplateVersionRepository.get_by_id(request.template_version_id, org_id)
        if not version_doc:
            raise NotFoundError(message="Template version not found", code="TEMPLATE_VERSION_NOT_FOUND")
        if version_doc.get("status") != "published":
            raise ValidationError(
                message="Template version must be published before issuing certificates",
                code="TEMPLATE_NOT_PUBLISHED",
            )
        template_id = str(version_doc.get("template_id"))

        # 2. Validate import
        import_doc = await ImportRepository.get_by_id(request.import_id, org_id)
        if not import_doc:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")
        if import_doc.get("status") not in ("ready", "validated"):
            raise ValidationError(
                message=f"Import must be in 'ready' or 'validated' status (current: {import_doc.get('status')})",
                code="IMPORT_NOT_READY",
            )

        # 3. Check organization concurrent job quota
        active_jobs = await IssuanceJobRepository.count_active_jobs(org_id)
        if active_jobs >= settings.MAX_ACTIVE_JOBS_PER_ORG:
            raise ValidationError(
                message=f"Maximum active jobs limit ({settings.MAX_ACTIVE_JOBS_PER_ORG}) reached for this organization.",
                code="JOB_QUOTA_EXCEEDED",
            )

        # 4. Fetch valid rows from import
        valid_rows, total_valid = await ImportRowRepository.list_rows(
            import_id=request.import_id,
            organization_id=org_id,
            page=1,
            limit=50000,
            status="valid",
        )
        if not valid_rows or total_valid == 0:
            raise ValidationError(
                message="Import contains no valid rows for certificate issuance",
                code="NO_VALID_RECIPIENTS",
            )

        # 4b. Check certificate quota for bulk issuance — P10
        from app.services.quota_service import QuotaService
        await QuotaService.check_certificate_quota(org_id=org_id, quantity=len(valid_rows))

        # 5. Create Issuance Job in database
        job_doc = await IssuanceJobRepository.create(
            organization_id=org_id,
            template_id=template_id,
            template_version_id=request.template_version_id,
            import_id=request.import_id,
            total=len(valid_rows),
            created_by=user_id,
        )
        job_id = job_doc["id"]

        # 6. Bulk create job items
        items_count = await IssuanceItemRepository.bulk_create(
            job_id=job_id,
            organization_id=org_id,
            valid_rows=valid_rows,
        )
        logger.info("Created %d job items for issuance job %s", items_count, job_id)

        # 7. Audit log creation event
        await AuditLogRepository.log_event(
            action="issuance_job.created",
            resource_type="issuance_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={
                "total_items": items_count,
                "template_version_id": request.template_version_id,
                "import_id": request.import_id,
            },
        )

        # 8. Queue ARQ task in Redis — P12.02: No web-server background execution fallback in production
        queued = await QueueManager.enqueue(TASK_GENERATE_BULK_CERTIFICATES, job_id, org_id)
        if not queued:
            if settings.APP_ENV in ("production", "staging"):
                logger.error("Failed to enqueue bulk issuance job %s: Redis queue is unavailable", job_id)
                await IssuanceJobRepository.update_status(
                    job_id,
                    "failed",
                    error={"code": "QUEUE_UNAVAILABLE", "message": "Background job queue is unavailable"}
                )
                from app.core.exceptions import AppException
                raise AppException(
                    code="QUEUE_UNAVAILABLE",
                    message="Background job processing queue is currently unavailable. Please try again shortly.",
                    status_code=503,
                )
            else:
                logger.info("Redis queue is unavailable in %s environment; job %s remains queued", settings.APP_ENV, job_id)

        return IssuanceJobResponse(**job_doc)

    @classmethod
    async def get_job(cls, job_id: str, org_id: str) -> IssuanceJobResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")
        return IssuanceJobResponse(**job)

    @classmethod
    async def list_jobs(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> IssuanceJobListResponse:
        items, total = await IssuanceJobRepository.list_jobs(
            organization_id=org_id,
            page=page,
            limit=limit,
            status=status,
        )
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        return IssuanceJobListResponse(
            items=[IssuanceJobResponse(**j) for j in items],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    @classmethod
    async def pause_job(cls, job_id: str, org_id: str, user_id: str) -> IssuanceJobResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        if job["status"] not in ("queued", "starting", "processing"):
            raise ValidationError(
                message=f"Cannot pause job in '{job['status']}' state",
                code="INVALID_JOB_STATE",
            )

        updated = await IssuanceJobRepository.update_status(job_id, "paused", org_id)
        await AuditLogRepository.log_event(
            action="issuance_job.paused",
            resource_type="issuance_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
        )
        return IssuanceJobResponse(**updated)

    @classmethod
    async def resume_job(cls, job_id: str, org_id: str, user_id: str) -> IssuanceJobResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        if job["status"] != "paused":
            raise ValidationError(
                message=f"Cannot resume job that is not paused (current: '{job['status']}')",
                code="INVALID_JOB_STATE",
            )

        updated = await IssuanceJobRepository.update_status(job_id, "queued", org_id)

        # Re-enqueue worker
        queued = await QueueManager.enqueue(TASK_GENERATE_BULK_CERTIFICATES, job_id, org_id)
        if not queued:
            import asyncio
            from app.workers.certificate_worker import generate_bulk_certificates_task
            asyncio.create_task(generate_bulk_certificates_task(None, job_id, org_id))

        await AuditLogRepository.log_event(
            action="issuance_job.resumed",
            resource_type="issuance_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
        )
        return IssuanceJobResponse(**updated)

    @classmethod
    async def cancel_job(cls, job_id: str, org_id: str, user_id: str) -> IssuanceJobResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        if job["status"] in ("completed", "cancelled"):
            raise ValidationError(
                message=f"Cannot cancel job in '{job['status']}' state",
                code="INVALID_JOB_STATE",
            )

        # Cancel remaining pending items — generated certs remain untouched!
        cancelled_count = await IssuanceItemRepository.cancel_pending_items(job_id)
        logger.info("Cancelled %d pending items for job %s", cancelled_count, job_id)

        # Recalculate counts & set status = cancelled
        await IssuanceJobRepository.sync_counts_from_items(job_id)
        updated = await IssuanceJobRepository.update_status(job_id, "cancelled", org_id)

        await AuditLogRepository.log_event(
            action="issuance_job.cancelled",
            resource_type="issuance_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"cancelled_items": cancelled_count},
        )
        return IssuanceJobResponse(**updated)

    @classmethod
    async def retry_failed(cls, job_id: str, org_id: str, user_id: str) -> IssuanceJobResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        reset_count = await IssuanceItemRepository.reset_failed_to_pending(job_id)
        if reset_count == 0:
            raise ValidationError(
                message="No failed items found to retry in this job",
                code="NO_FAILED_ITEMS",
            )

        # Update job counts & transition back to queued
        await IssuanceJobRepository.sync_counts_from_items(job_id)
        updated = await IssuanceJobRepository.update_status(job_id, "queued", org_id)

        # Re-enqueue worker
        queued = await QueueManager.enqueue(TASK_GENERATE_BULK_CERTIFICATES, job_id, org_id)
        if not queued:
            import asyncio
            from app.workers.certificate_worker import generate_bulk_certificates_task
            asyncio.create_task(generate_bulk_certificates_task(None, job_id, org_id))

        await AuditLogRepository.log_event(
            action="issuance_job.retry_started",
            resource_type="issuance_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"retried_items": reset_count},
        )
        return IssuanceJobResponse(**updated)

    @classmethod
    async def retry_single_item(
        cls,
        job_id: str,
        item_id: str,
        org_id: str,
        user_id: str,
    ) -> IssuanceItemResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        item = await IssuanceItemRepository.reset_single_item_to_pending(item_id, job_id)
        if not item:
            raise NotFoundError(message="Failed job item not found or item is not in failed status", code="ITEM_NOT_FOUND")

        # Sync counts
        await IssuanceJobRepository.sync_counts_from_items(job_id)
        if job["status"] in ("completed", "completed_with_errors"):
            await IssuanceJobRepository.update_status(job_id, "queued", org_id)

        # Re-enqueue worker
        queued = await QueueManager.enqueue(TASK_GENERATE_BULK_CERTIFICATES, job_id, org_id)
        if not queued:
            import asyncio
            from app.workers.certificate_worker import generate_bulk_certificates_task
            asyncio.create_task(generate_bulk_certificates_task(None, job_id, org_id))

        return IssuanceItemResponse(**item)

    @classmethod
    async def list_items(
        cls,
        job_id: str,
        org_id: str,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> IssuanceItemListResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        items, total = await IssuanceItemRepository.list_items(
            job_id=job_id,
            status=status,
            recipient_search=search,
            page=page,
            limit=limit,
        )
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        return IssuanceItemListResponse(
            items=[IssuanceItemResponse(**i) for i in items],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    @classmethod
    async def get_errors(cls, job_id: str, org_id: str) -> List[ErrorRowItem]:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        failed_items = await IssuanceItemRepository.get_failed_items(job_id)
        errors = []
        for item in failed_items:
            err = item.get("error") or {}
            recip = item.get("recipient") or {}
            errors.append(ErrorRowItem(
                row_number=item.get("row_number", 0),
                recipient_name=recip.get("name", ""),
                email=recip.get("email", ""),
                error_code=err.get("code", "UNKNOWN_ERROR"),
                error_message=err.get("message", "Unknown error"),
                attempts=item.get("attempts", 0),
            ))
        return errors

    @classmethod
    async def generate_errors_csv(cls, job_id: str, org_id: str) -> str:
        errors = await cls.get_errors(job_id, org_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["row_number", "recipient_name", "email", "error_code", "error_message", "attempts"])
        for err in errors:
            writer.writerow([
                err.row_number,
                err.recipient_name,
                err.email,
                err.error_code,
                err.error_message,
                err.attempts,
            ])
        return output.getvalue()
