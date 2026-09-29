from __future__ import annotations
import asyncio
import logging
from typing import Optional, Dict, Any

from app.core.config import settings
from app.repositories.issuance_job_repository import IssuanceJobRepository
from app.repositories.issuance_item_repository import IssuanceItemRepository
from app.services.certificate_service import CertificateService
from app.services.error_classifier import ErrorClassifier
from app.services.progress_service import ProgressService
from app.schemas.certificate import CertificateGenerateRequest

logger = logging.getLogger(__name__)


async def generate_bulk_certificates_task(
    ctx: Optional[Dict[str, Any]],
    job_id: str,
    org_id: str,
) -> Dict[str, Any]:
    """
    ARQ worker task: processes certificate generation for all pending items in an issuance job.
    Stateless, crash-safe, idempotent.
    """
    logger.info("Starting generate_bulk_certificates_task for job_id=%s, org_id=%s", job_id, org_id)

    # 1. Fetch job document
    job = await IssuanceJobRepository.get_by_id(job_id, org_id)
    if not job:
        logger.error("Job %s not found in org %s; aborting worker task.", job_id, org_id)
        return {"status": "error", "message": "Job not found"}

    if job.get("status") in ("cancelled", "paused"):
        logger.info("Job %s is currently %s; exiting task.", job_id, job.get("status"))
        return {"status": job.get("status")}

    # Update job status to processing
    await IssuanceJobRepository.update_status(job_id, "processing")

    # 2. Run crash recovery on stale items
    stale_recovered = await IssuanceItemRepository.reset_stale_processing_items(
        job_id=job_id,
        timeout_seconds=settings.RENDER_TIMEOUT_SECONDS,
        max_attempts=settings.MAX_ITEM_ATTEMPTS,
    )
    if stale_recovered > 0:
        logger.info("Recovered %d stale processing items for job %s", stale_recovered, job_id)

    template_version_id = job.get("template_version_id")
    import_id = job.get("import_id")
    user_id = job.get("created_by", "system")

    # Prefetch template assets and email settings ONCE per job — P12.01 & P12.15
    from app.repositories.template_version_repository import TemplateVersionRepository
    from app.repositories.email_settings_repository import EmailSettingsRepository
    from app.services.certificate_service import prefetch_template_assets

    preloaded_assets: dict[str, bytes] = {}
    if template_version_id:
        version_doc = await TemplateVersionRepository.get_by_id(str(template_version_id), org_id)
        if version_doc:
            preloaded_assets = await prefetch_template_assets(version_doc, org_id)

    email_settings = await EmailSettingsRepository.get_by_org(org_id)

    # 3. Main batch processing loop — P12.14 & P12.16
    processed_count = 0
    BATCH_SIZE = 20

    while True:
        # Check current job state before claiming next batch
        current_job = await IssuanceJobRepository.get_by_id(job_id)
        if not current_job or current_job.get("status") in ("cancelled", "paused"):
            logger.info("Job %s was %s; halting item claiming.", job_id, current_job.get("status") if current_job else "deleted")
            break

        # Atomically claim batch of pending items
        items = await IssuanceItemRepository.claim_batch(job_id, batch_size=BATCH_SIZE)
        if not items:
            # Fallback to single item claim
            single_item = await IssuanceItemRepository.claim_next(job_id)
            if not single_item:
                break
            items = [single_item]

        batch_completed = 0
        batch_failed = 0

        for item in items:
            item_id = item["id"]

            # Idempotency check: has this item already produced a certificate? (P12.18)
            if item.get("certificate_id"):
                logger.info("Item %s already has certificate %s; skipping render", item_id, item["certificate_id"])
                await IssuanceItemRepository.mark_completed(item_id, item["certificate_id"])
                batch_completed += 1
                continue

            # Deterministic idempotency key: unique per job and row/item (P12.18)
            row_identifier = item.get("import_row_id") or item_id
            idempotency_key = f"job_{job_id}_row_{row_identifier}"

            generate_req = CertificateGenerateRequest(
                template_version_id=template_version_id,
                data=item.get("data", {}),
                import_id=import_id,
                import_row_id=item.get("import_row_id"),
            )

            try:
                cert_res = await asyncio.wait_for(
                    CertificateService.generate(
                        request=generate_req,
                        org_id=org_id,
                        user_id=user_id,
                        idempotency_key=idempotency_key,
                        preloaded_assets=preloaded_assets,
                    ),
                    timeout=float(settings.RENDER_TIMEOUT_SECONDS),
                )
                await IssuanceItemRepository.mark_completed(item_id, cert_res.id)
                batch_completed += 1

                # P6: Auto-email using cached organization email settings (P12.15)
                try:
                    from app.services.email_service import EmailService
                    if email_settings and email_settings.get("auto_email_on_issuance"):
                        await EmailService.send_certificate_email(
                            certificate_id=cert_res.id,
                            org_id=org_id,
                            user_id=user_id,
                        )
                except Exception as email_err:
                    logger.warning("Auto-email trigger failed for cert %s: %s", cert_res.id, email_err)

            except asyncio.TimeoutError:
                logger.warning("Render timeout for item %s in job %s", item_id, job_id)
                err = {
                    "code": "RENDER_TIMEOUT",
                    "message": f"Certificate rendering timed out after {settings.RENDER_TIMEOUT_SECONDS}s",
                }
                await IssuanceItemRepository.mark_failed(item_id, err)
                batch_failed += 1

            except Exception as exc:
                err_code = getattr(exc, "code", "RENDER_ERROR")
                err_msg = str(getattr(exc, "message", str(exc)))[:500]
                err = {"code": err_code, "message": err_msg}
                category = ErrorClassifier.classify(err_code, err_msg)
                logger.warning("Generation error for item %s (%s): %s", item_id, category.value, err_msg)

                await IssuanceItemRepository.mark_failed(item_id, err)
                batch_failed += 1

        # Batch progress update: single atomic write for entire batch (P12.16)
        if batch_completed > 0 or batch_failed > 0:
            await IssuanceJobRepository.increment_counts(
                job_id,
                inc_completed=batch_completed,
                inc_failed=batch_failed,
                inc_pending=-(batch_completed + batch_failed),
            )
            processed_count += batch_completed

    # 4. Finalize job if all items processed (P12.19)
    await ProgressService.finalize_job_if_done(job_id)
    logger.info("generate_bulk_certificates_task completed for job_id=%s. Processed %d items in this run.", job_id, processed_count)

    return {"status": "ok", "job_id": job_id, "processed_items": processed_count}
