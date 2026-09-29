"""
Worker & Queue Metrics Engine — P12.24.
Aggregates queue depths, active jobs, items in processing, failure rates, and dead-letter outbox events.
"""
from __future__ import annotations
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.core.database import DatabaseManager
from app.queue.redis import QueueManager
from app.repositories.outbox_repository import OutboxRepository

logger = logging.getLogger(__name__)


class QueueMetricsService:
    @classmethod
    async def get_metrics(cls, org_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Aggregate operational queue & worker metrics across MongoDB and Redis.
        """
        db = DatabaseManager.get_db()
        now = datetime.now(timezone.utc)

        # 1. Job level metrics
        job_match: Dict[str, Any] = {}
        if org_id:
            try:
                job_match["organization_id"] = ObjectId(org_id)
            except Exception:
                pass

        jobs_col = db["issuance_jobs"]
        pending_jobs = await jobs_col.count_documents({**job_match, "status": "pending"})
        processing_jobs = await jobs_col.count_documents({**job_match, "status": "processing"})
        completed_jobs = await jobs_col.count_documents({**job_match, "status": "completed"})
        failed_jobs = await jobs_col.count_documents({**job_match, "status": {"$in": ["failed", "completed_with_errors", "partially_failed"]}})

        # 2. Item level metrics (queue depth)
        items_col = db["issuance_items"]
        item_match: Dict[str, Any] = {}
        if org_id:
            try:
                item_match["organization_id"] = ObjectId(org_id)
            except Exception:
                pass

        pending_items = await items_col.count_documents({**item_match, "status": "pending"})
        processing_items = await items_col.count_documents({**item_match, "status": "processing"})
        completed_items = await items_col.count_documents({**item_match, "status": "completed"})
        failed_items = await items_col.count_documents({**item_match, "status": "failed"})

        # 3. Outbox & Dead-letter metrics
        outbox_col = db["outbox_events"]
        outbox_match: Dict[str, Any] = {}
        if org_id:
            try:
                outbox_match["organization_id"] = ObjectId(org_id)
            except Exception:
                pass

        pending_outbox = await outbox_col.count_documents({**outbox_match, "status": "pending"})
        dead_letter_outbox = await outbox_col.count_documents({**outbox_match, "status": "dead_letter"})

        # 4. Redis connection status
        redis_healthy = False
        pool = await QueueManager.get_pool()
        if pool is not None:
            try:
                await pool.ping()
                redis_healthy = True
            except Exception:
                redis_healthy = False

        return {
            "timestamp": now.isoformat(),
            "redis_connected": redis_healthy,
            "jobs": {
                "pending": pending_jobs,
                "processing": processing_jobs,
                "completed": completed_jobs,
                "failed": failed_jobs,
                "active_total": pending_jobs + processing_jobs,
            },
            "items": {
                "queue_depth_pending": pending_items,
                "in_flight_processing": processing_items,
                "completed": completed_items,
                "failed": failed_items,
                "total": pending_items + processing_items + completed_items + failed_items,
            },
            "outbox": {
                "pending_events": pending_outbox,
                "dead_letter_events": dead_letter_outbox,
            },
        }
