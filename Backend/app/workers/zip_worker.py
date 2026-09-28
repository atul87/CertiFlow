from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from app.services.zip_service import ZipService

logger = logging.getLogger(__name__)


async def create_zip_task(
    ctx: Optional[Dict[str, Any]],
    job_id: str,
    org_id: str,
) -> Dict[str, Any]:
    """
    ARQ worker task: generates a zip archive of all certificates for an issuance job.
    """
    logger.info("Starting create_zip_task for job_id=%s, org_id=%s", job_id, org_id)
    try:
        res = await ZipService.generate_zip(job_id, org_id)
        return {"status": "ok", "job_id": job_id, "zip_info": res}
    except Exception as exc:
        logger.exception("create_zip_task failed for job_id=%s: %s", job_id, exc)
        return {"status": "failed", "job_id": job_id, "error": str(exc)}
