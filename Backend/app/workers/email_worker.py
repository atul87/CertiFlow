from __future__ import annotations
import asyncio
import logging
from typing import Optional, Dict, Any

from app.core.config import settings
from app.repositories.email_job_repository import EmailJobRepository
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.services.email_delivery_service import EmailDeliveryService

logger = logging.getLogger(__name__)


async def send_certificate_email_task(ctx: Optional[Dict[str, Any]], delivery_id: str) -> Optional[Dict[str, Any]]:
    """ARQ task to process a single certificate email delivery."""
    logger.info(f"[EmailWorker] Starting delivery task for {delivery_id}")
    try:
        res = await EmailDeliveryService.process_delivery(delivery_id)
        logger.info(f"[EmailWorker] Finished delivery task for {delivery_id}: {res.get('status') if res else 'None'}")
        return res
    except Exception as e:
        logger.exception(f"[EmailWorker] Unhandled error processing delivery {delivery_id}: {e}")
        return None


async def process_bulk_email_job_task(ctx: Optional[Dict[str, Any]], job_id: str, org_id: str) -> Optional[Dict[str, Any]]:
    """ARQ task to process a bulk email issuance job."""
    logger.info(f"[EmailWorker] Starting bulk email job task for {job_id}")
    job = await EmailJobRepository.get_by_id(job_id, org_id)
    if not job:
        logger.error(f"[EmailWorker] Bulk email job {job_id} not found")
        return None

    if job.get("status") in ("cancelled", "paused"):
        logger.info(f"[EmailWorker] Job {job_id} is in status {job.get('status')}, exiting")
        return job

    await EmailJobRepository.update_status(job_id, "processing")

    # Fetch queued deliveries for this job
    # Fetch in batches to support controlled concurrency
    limit = 50
    page = 1
    concurrency = settings.EMAIL_WORKER_CONCURRENCY or 5
    semaphore = asyncio.Semaphore(concurrency)

    async def _process_single(deliv_id: str):
        async with semaphore:
            await EmailDeliveryService.process_delivery(deliv_id)

    while True:
        # Check if job was paused or cancelled mid-execution
        fresh_job = await EmailJobRepository.get_by_id(job_id, org_id)
        if fresh_job and fresh_job.get("status") in ("cancelled", "paused"):
            logger.info(f"[EmailWorker] Bulk job {job_id} was {fresh_job.get('status')}")
            break

        deliveries, total = await EmailDeliveryRepository.list_deliveries(
            organization_id=org_id,
            email_job_id=job_id,
            status="queued",
            page=1,
            limit=limit,
        )
        if not deliveries:
            break

        tasks = [_process_single(d["id"]) for d in deliveries]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Brief rate limiting pause between batches
        await asyncio.sleep(0.05)

    final_job = await EmailJobRepository.get_by_id(job_id, org_id)
    logger.info(f"[EmailWorker] Completed bulk email job {job_id} with status {final_job.get('status') if final_job else 'unknown'}")
    return final_job
