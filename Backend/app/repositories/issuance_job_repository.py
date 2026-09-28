from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class IssuanceJobRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("issuance_jobs")

    @classmethod
    async def create(
        cls,
        organization_id: str,
        template_id: str,
        template_version_id: str,
        import_id: str,
        total: int,
        created_by: str,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "template_id": ObjectId(template_id),
            "template_version_id": ObjectId(template_version_id),
            "import_id": ObjectId(import_id),
            "status": "queued",
            "total": total,
            "pending": total,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "progress": 0.0,
            "created_by": ObjectId(created_by),
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "zip_info": None,
            "error": None,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        s["organization_id"] = str(doc.get("organization_id", ""))
        s["template_id"] = str(doc.get("template_id", ""))
        s["template_version_id"] = str(doc.get("template_version_id", ""))
        s["import_id"] = str(doc.get("import_id", ""))
        s["created_by"] = str(doc.get("created_by", ""))
        return s

    @classmethod
    async def get_by_id(cls, job_id: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        query: Dict[str, Any] = {"_id": jid}
        if organization_id:
            try:
                query["organization_id"] = ObjectId(organization_id)
            except Exception:
                return None

        doc = await cls._collection().find_one(query)
        if not doc:
            return None
        return cls._serialize(doc)

    @classmethod
    async def list_jobs(
        cls,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0

        query: Dict[str, Any] = {"organization_id": oid}
        if status:
            query["status"] = status

        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)

        return [cls._serialize(doc) for doc in items], total

    @classmethod
    async def update_status(
        cls,
        job_id: str,
        status: str,
        organization_id: Optional[str] = None,
        **extra_fields: Any
    ) -> Optional[Dict[str, Any]]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        query: Dict[str, Any] = {"_id": jid}
        if organization_id:
            try:
                query["organization_id"] = ObjectId(organization_id)
            except Exception:
                return None

        update_dict: Dict[str, Any] = {"status": status, **extra_fields}
        now = datetime.now(timezone.utc)
        if status == "processing" and "started_at" not in update_dict:
            update_dict["started_at"] = now
        elif status in ("completed", "completed_with_errors", "failed", "cancelled") and "completed_at" not in update_dict:
            update_dict["completed_at"] = now

        res = await cls._collection().find_one_and_update(
            query,
            {"$set": update_dict},
            return_document=True,
        )
        if not res:
            return None
        return cls._serialize(res)

    @classmethod
    async def count_active_jobs(cls, organization_id: str) -> int:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return 0
        return await cls._collection().count_documents({
            "organization_id": oid,
            "status": {"$in": ["queued", "starting", "processing"]}
        })

    @classmethod
    async def increment_counts(
        cls,
        job_id: str,
        inc_completed: int = 0,
        inc_failed: int = 0,
        inc_processing: int = 0,
        inc_pending: int = 0,
        inc_cancelled: int = 0,
    ) -> Optional[Dict[str, Any]]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        inc_dict: Dict[str, int] = {}
        if inc_completed:
            inc_dict["completed"] = inc_completed
        if inc_failed:
            inc_dict["failed"] = inc_failed
        if inc_processing:
            inc_dict["processing"] = inc_processing
        if inc_pending:
            inc_dict["pending"] = inc_pending
        if inc_cancelled:
            inc_dict["cancelled"] = inc_cancelled

        if not inc_dict:
            doc = await cls._collection().find_one({"_id": jid})
            return cls._serialize(doc) if doc else None

        res = await cls._collection().find_one_and_update(
            {"_id": jid},
            {"$inc": inc_dict},
            return_document=True,
        )
        if not res:
            return None

        # Update progress percentage
        total = res.get("total", 0)
        done = res.get("completed", 0) + res.get("failed", 0) + res.get("cancelled", 0)
        progress = round(min(100.0, (done / total * 100.0)), 2) if total > 0 else 0.0

        res = await cls._collection().find_one_and_update(
            {"_id": jid},
            {"$set": {"progress": progress}},
            return_document=True,
        )
        return cls._serialize(res) if res else None

    @classmethod
    async def sync_counts_from_items(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """Recalculate and update job counts from items collection."""
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        items_col = DatabaseManager.get_collection("issuance_job_items")
        pipeline = [
            {"$match": {"job_id": jid}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        cursor = items_col.aggregate(pipeline)
        counts = {item["_id"]: item["count"] async for item in cursor}

        pending = counts.get("pending", 0)
        processing = counts.get("processing", 0)
        completed = counts.get("completed", 0)
        failed = counts.get("failed", 0)
        cancelled = counts.get("cancelled", 0)
        total = pending + processing + completed + failed + cancelled

        done = completed + failed + cancelled
        progress = round(min(100.0, (done / total * 100.0)), 2) if total > 0 else 0.0

        update_fields: Dict[str, Any] = {
            "total": total,
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "progress": progress,
        }

        res = await cls._collection().find_one_and_update(
            {"_id": jid},
            {"$set": update_fields},
            return_document=True,
        )
        return cls._serialize(res) if res else None

    @classmethod
    async def update_zip_info(cls, job_id: str, zip_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        res = await cls._collection().find_one_and_update(
            {"_id": jid},
            {"$set": {"zip_info": zip_info}},
            return_document=True,
        )
        return cls._serialize(res) if res else None
