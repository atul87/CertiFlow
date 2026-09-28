from __future__ import annotations
import os
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.repositories.report_job_repository import ReportJobRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.analytics.date_range_helper import DateRangeHelper
from app.services.reports.csv_report_generator import CSVReportGenerator
from app.services.reports.pdf_report_generator import PDFReportGenerator
from app.services.signed_url_service import SignedUrlService
from app.services.storage_service import StorageService
from app.queue.redis import QueueManager
from app.queue.tasks import TASK_GENERATE_REPORT

logger = logging.getLogger(__name__)


class ReportService:

    @classmethod
    async def create_report(
        cls,
        org_id: str,
        report_type: str,
        format_type: str,
        filters: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        # 1. Resolve date filters
        date_range = filters.get("date_range", "last_30_days")
        start_date, end_date, _, _ = DateRangeHelper.resolve_range(
            preset=date_range,
            from_date=filters.get("from_date"),
            to_date=filters.get("to_date"),
        )
        resolved_filters = {
            **filters,
            "start_date": start_date,
            "end_date": end_date,
            "date_range": date_range,
        }

        # 2. Create DB record
        job_doc = await ReportJobRepository.create(
            organization_id=org_id,
            report_type=report_type,
            format_type=format_type,
            filters=resolved_filters,
            created_by=user_id,
        )
        job_id = job_doc["id"]

        # 3. Audit log
        await AuditLogRepository.log_event(
            action="report_job.created",
            resource_type="report_job",
            resource_id=job_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"type": report_type, "format": format_type},
        )

        # 4. Enqueue background task
        queued = await QueueManager.enqueue(TASK_GENERATE_REPORT, job_id, org_id)
        if not queued and settings.APP_ENV != "test":
            from app.workers.report_worker import generate_report_task
            asyncio.create_task(generate_report_task(None, job_id, org_id))

        return job_doc

    @classmethod
    async def process_report(cls, report_job_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        job = await ReportJobRepository.get_by_id(report_job_id, org_id)
        if not job:
            logger.error(f"[ReportService] Job {report_job_id} not found")
            return None

        await ReportJobRepository.update_status(report_job_id, "processing")
        report_type = job["type"]
        fmt = job["format"]
        filters = job.get("filters", {})

        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        if not start_date or not end_date:
            start_date, end_date, _, _ = DateRangeHelper.resolve_range(preset="last_30_days")

        try:
            file_bytes = b""
            row_count = 0

            if fmt == "csv":
                if report_type == "certificate_report":
                    file_bytes, row_count = await CSVReportGenerator.generate_certificate_csv(org_id, filters)
                elif report_type == "email_report":
                    file_bytes, row_count = await CSVReportGenerator.generate_email_csv(org_id, filters)
                elif report_type == "verification_report":
                    file_bytes, row_count = await CSVReportGenerator.generate_verification_csv(org_id, filters)
                elif report_type == "activity_report":
                    file_bytes, row_count = await CSVReportGenerator.generate_activity_csv(org_id, filters)
                else:
                    file_bytes, row_count = await CSVReportGenerator.generate_certificate_csv(org_id, filters)
            elif fmt == "pdf":
                file_bytes = await PDFReportGenerator.generate_summary_pdf(org_id, start_date, end_date)
                row_count = 1

            # Save report to storage
            filename = f"report_{report_type}_{report_job_id}.{fmt}"
            rel_dir = Path("reports") / org_id
            target_dir = StorageService.get_base_dir() / rel_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / filename
            with open(target_path, "wb") as f:
                f.write(file_bytes)

            storage_key = str((rel_dir / filename).as_posix())
            file_size = len(file_bytes)

            updated = await ReportJobRepository.update_status(
                job_id=report_job_id,
                status="completed",
                storage_key=storage_key,
                row_count=row_count,
                file_size_bytes=file_size,
            )
            return updated

        except Exception as e:
            logger.exception(f"[ReportService] Error generating report {report_job_id}: {e}")
            return await ReportJobRepository.update_status(
                job_id=report_job_id,
                status="failed",
                error=str(e),
            )

    @classmethod
    async def get_report(cls, report_job_id: str, org_id: str) -> Dict[str, Any]:
        job = await ReportJobRepository.get_by_id(report_job_id, org_id)
        if not job:
            raise NotFoundError(message="Report job not found", code="REPORT_NOT_FOUND")

        # Attach signed download URL if completed
        if job.get("status") == "completed" and job.get("storage_key"):
            token = SignedUrlService.generate_token(report_job_id, expires_in_seconds=settings.REPORT_EXPIRY_HOURS * 3600)
            job["download_url"] = f"{settings.BASE_URL}/api/v1/reports/{report_job_id}/download?token={token}"

        return job

    @classmethod
    async def list_reports(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[list, int]:
        items, total = await ReportJobRepository.list_jobs(org_id, page, limit)
        for job in items:
            if job.get("status") == "completed" and job.get("storage_key"):
                token = SignedUrlService.generate_token(job["id"], expires_in_seconds=settings.REPORT_EXPIRY_HOURS * 3600)
                job["download_url"] = f"{settings.BASE_URL}/api/v1/reports/{job['id']}/download?token={token}"
        return items, total

    @classmethod
    async def get_report_file_bytes(cls, report_job_id: str, org_id: str, token: Optional[str] = None) -> Tuple[bytes, str, str]:
        """Verify report ownership and download token, returning (content_bytes, filename, media_type)."""
        job = await ReportJobRepository.get_by_id(report_job_id, org_id)
        if not job:
            raise NotFoundError(message="Report job not found", code="REPORT_NOT_FOUND")

        if token:
            if not SignedUrlService.verify_token(report_job_id, token):
                raise ForbiddenError(message="Invalid or expired report download link", code="INVALID_SIGNED_URL")

        if job.get("status") != "completed":
            raise ValidationError(message=f"Report is in status {job.get('status')}", code="REPORT_NOT_READY")

        storage_key = job.get("storage_key")
        if not storage_key:
            raise NotFoundError(message="Report file not found", code="FILE_NOT_FOUND")

        content = StorageService.read_file(storage_key)
        if not content:
            raise NotFoundError(message="Report file missing from storage", code="FILE_NOT_FOUND")

        fmt = job.get("format", "csv")
        media_type = "text/csv" if fmt == "csv" else "application/pdf"
        filename = f"report_{job.get('type')}_{report_job_id}.{fmt}"

        return content, filename, media_type
