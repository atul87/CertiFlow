from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from app.core.exceptions import NotFoundError
from app.repositories.issuance_job_repository import IssuanceJobRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.issuance import IssuanceJobProgressResponse

logger = logging.getLogger(__name__)


class ProgressService:
    @staticmethod
    def calculate_progress_percentage(total: int, completed: int, failed: int, cancelled: int = 0) -> float:
        """
        Progress formula: (completed + failed + cancelled) / total * 100
        Ensures failed items also advance progress so the UI doesn't appear stuck.
        """
        if total <= 0:
            return 0.0
        done = completed + failed + cancelled
        pct = (done / total) * 100.0
        return round(min(100.0, max(0.0, pct)), 2)

    @classmethod
    async def get_progress(cls, job_id: str, org_id: str) -> IssuanceJobProgressResponse:
        job = await IssuanceJobRepository.get_by_id(job_id, org_id)
        if not job:
            raise NotFoundError(message="Issuance job not found", code="JOB_NOT_FOUND")

        total = job.get("total", 0)
        completed = job.get("completed", 0)
        failed = job.get("failed", 0)
        pending = job.get("pending", 0)
        processing = job.get("processing", 0)
        cancelled = job.get("cancelled", 0)

        progress = cls.calculate_progress_percentage(total, completed, failed, cancelled)

        return IssuanceJobProgressResponse(
            job_id=job["id"],
            status=job.get("status", "unknown"),
            total=total,
            completed=completed,
            processing=processing,
            failed=failed,
            pending=pending,
            cancelled=cancelled,
            progress=progress,
        )

    @classmethod
    async def finalize_job_if_done(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Checks if all items in the job have completed processing.
        If pending == 0 and processing == 0, transitions status to completed or completed_with_errors.
        """
        job = await IssuanceJobRepository.sync_counts_from_items(job_id)
        if not job:
            return None

        status = job.get("status")
        if status in ("completed", "completed_with_errors", "cancelled", "paused"):
            return job

        pending = job.get("pending", 0)
        processing = job.get("processing", 0)
        total = job.get("total", 0)
        completed = job.get("completed", 0)
        failed = job.get("failed", 0)

        if pending == 0 and processing == 0:
            if failed > 0:
                final_status = "completed_with_errors"
            else:
                final_status = "completed"

            updated = await IssuanceJobRepository.update_status(
                job_id=job_id,
                status=final_status,
            )
            logger.info("Job %s finalized with status: %s (completed=%d, failed=%d, total=%d)", job_id, final_status, completed, failed, total)

            # Audit log
            org_id = job.get("organization_id")
            user_id = job.get("created_by")
            if org_id and user_id:
                await AuditLogRepository.log_event(
                    action=f"issuance_job.{final_status}",
                    resource_type="issuance_job",
                    resource_id=job_id,
                    organization_id=org_id,
                    user_id=user_id,
                    metadata={
                        "total": total,
                        "completed": completed,
                        "failed": failed,
                    }
                )

            return updated

        return job
