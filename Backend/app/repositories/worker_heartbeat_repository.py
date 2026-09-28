from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from app.core.database import DatabaseManager


class WorkerHeartbeatRepository:
    COLLECTION_NAME = "worker_heartbeats"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def upsert_heartbeat(
        cls,
        worker_id: str,
        worker_type: str,
        status: str = "idle",
        current_job_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record or update a worker's liveness heartbeat."""
        now = datetime.now(timezone.utc)
        doc = {
            "worker_id": worker_id,
            "worker_type": worker_type,
            "status": status,
            "current_job_id": current_job_id,
            "last_seen": now,
            "metadata": metadata or {}
        }
        await cls._collection().update_one(
            {"worker_id": worker_id},
            {"$set": doc},
            upsert=True
        )
        return doc

    @classmethod
    async def list_active_workers(cls, timeout_seconds: int = 60) -> List[Dict[str, Any]]:
        """List all workers seen within timeout_seconds."""
        threshold = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)
        cursor = cls._collection().find({"last_seen": {"$gte": threshold}})
        return await cursor.to_list(length=100)

    @classmethod
    async def find_dead_workers(cls, timeout_seconds: int = 60) -> List[Dict[str, Any]]:
        """Find workers whose last heartbeat is older than timeout_seconds."""
        threshold = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)
        cursor = cls._collection().find({"last_seen": {"$lt": threshold}})
        return await cursor.to_list(length=100)

    @classmethod
    async def remove_worker(cls, worker_id: str) -> bool:
        """Remove a worker record upon graceful shutdown."""
        res = await cls._collection().delete_one({"worker_id": worker_id})
        return res.deleted_count > 0
