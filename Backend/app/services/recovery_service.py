"""
Recovery Service (P9 Reliability).
Monitors worker heartbeats, detects stuck/crashed background jobs,
requeues retryable work, and transitions unrecoverable tasks to dead-letter status.
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.core.database import DatabaseManager
from app.repositories.worker_heartbeat_repository import WorkerHeartbeatRepository

logger = logging.getLogger(__name__)


class RecoveryService:
    @classmethod
    async def record_worker_heartbeat(
        cls,
        worker_id: str,
        worker_type: str,
        status: str = "idle",
        current_job_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record or refresh a worker process's liveness heartbeat."""
        return await WorkerHeartbeatRepository.upsert_heartbeat(
            worker_id=worker_id,
            worker_type=worker_type,
            status=status,
            current_job_id=current_job_id,
            metadata=metadata
        )

    @classmethod
    async def recover_stuck_jobs(
        cls,
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Scans background jobs currently stuck in 'processing' status longer than timeout_seconds.
        If retry count < max_retries, resets them to 'pending' to be picked up again.
        Otherwise marks them as permanently failed (dead-letter).
        """
        timeout = timeout_seconds or settings.STUCK_JOB_TIMEOUT_SECONDS
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout)
        recovered_count = 0
        dead_letter_count = 0

        # 1. Recover stuck Issuance Jobs
        issuance_coll = DatabaseManager.get_collection("issuance_jobs")
        stuck_issuance_cursor = issuance_coll.find({
            "status": "processing",
            "updated_at": {"$lt": cutoff}
        })
        async for job in stuck_issuance_cursor:
            retries = job.get("retry_count", 0)
            if retries >= 3:
                await issuance_coll.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "failed",
                            "error": "Job timed out and exceeded maximum recovery retry attempts (dead-letter)",
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                dead_letter_count += 1
            else:
                await issuance_coll.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "pending",
                            "updated_at": datetime.now(timezone.utc)
                        },
                        "$inc": {"retry_count": 1}
                    }
                )
                recovered_count += 1

        # 2. Recover stuck Email Jobs
        email_job_coll = DatabaseManager.get_collection("email_jobs")
        stuck_email_cursor = email_job_coll.find({
            "status": "processing",
            "updated_at": {"$lt": cutoff}
        })
        async for job in stuck_email_cursor:
            retries = job.get("retry_count", 0)
            if retries >= 3:
                await email_job_coll.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "failed",
                            "error": "Email job exceeded maximum recovery retry attempts",
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                dead_letter_count += 1
            else:
                await email_job_coll.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "pending",
                            "updated_at": datetime.now(timezone.utc)
                        },
                        "$inc": {"retry_count": 1}
                    }
                )
                recovered_count += 1

        # 3. Recover stuck Report Jobs
        report_job_coll = DatabaseManager.get_collection("report_jobs")
        stuck_report_cursor = report_job_coll.find({
            "status": "processing",
            "updated_at": {"$lt": cutoff}
        })
        async for job in stuck_report_cursor:
            retries = job.get("retry_count", 0)
            if retries >= 3:
                await report_job_coll.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "failed",
                            "error": "Report job exceeded maximum retry attempts",
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                dead_letter_count += 1
            else:
                await report_job_coll.update_one(
                    {"_id": job["_id"]},
                    {
                        "$set": {
                            "status": "pending",
                            "updated_at": datetime.now(timezone.utc)
                        },
                        "$inc": {"retry_count": 1}
                    }
                )
                recovered_count += 1

        logger.info(
            f"Stuck job recovery completed: recovered={recovered_count}, dead_letter={dead_letter_count}"
        )
        return {
            "recovered": recovered_count,
            "dead_letter": dead_letter_count
        }

    @classmethod
    async def get_worker_status(cls) -> Dict[str, Any]:
        """Summary of active and dead worker processes."""
        active = await WorkerHeartbeatRepository.list_active_workers(timeout_seconds=60)
        dead = await WorkerHeartbeatRepository.find_dead_workers(timeout_seconds=60)
        return {
            "active_count": len(active),
            "dead_count": len(dead),
            "active_workers": [
                {
                    "worker_id": w["worker_id"],
                    "worker_type": w["worker_type"],
                    "status": w.get("status", "idle"),
                    "last_seen": w.get("last_seen").isoformat() if w.get("last_seen") else None
                }
                for w in active
            ]
        }
