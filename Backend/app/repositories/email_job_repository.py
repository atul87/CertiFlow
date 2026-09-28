from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from pymongo import ReturnDocument
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class EmailJobRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("email_jobs")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        for field in ("organization_id", "template_id", "created_by"):
            if doc.get(field):
                s[field] = str(doc[field])
        total = s.get("total", 0)
        sent = s.get("sent", 0)
        failed = s.get("failed", 0)
        bounced = s.get("bounced", 0)
        processed = sent + failed + bounced
        s["progress"] = round((processed / total * 100.0), 2) if total > 0 else 0.0
        return s

    @classmethod
    async def create(
        cls,
        organization_id: str,
        total: int,
        template_id: Optional[str],
        delivery_mode: str,
        created_by: str,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "template_id": ObjectId(template_id) if template_id else None,
            "delivery_mode": delivery_mode,
            "status": "queued",
            "total": total,
            "queued": total,
            "sending": 0,
            "sent": 0,
            "delivered": 0,
            "failed": 0,
            "bounced": 0,
            "created_by": ObjectId(created_by),
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "completed_at": None,
            "error": None,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_id(
        cls,
        job_id: str,
        organization_id: Optional[str] = None,
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
        doc = await cls._collection().find_one(query)
        return cls._serialize(doc) if doc else None

    @classmethod
    async def list_jobs(
        cls,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0
        query = {"organization_id": oid}
        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        return [cls._serialize(d) for d in items], total

    @classmethod
    async def update_status(
        cls,
        job_id: str,
        status: str,
        error: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        updates: Dict[str, Any] = {
            "status": status,
            "updated_at": now,
        }
        if status in ("starting", "processing"):
            updates["started_at"] = now
        elif status in ("completed", "completed_with_errors", "failed", "cancelled"):
            updates["completed_at"] = now
        if error:
            updates["error"] = error

        doc = await cls._collection().find_one_and_update(
            {"_id": jid},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def record_delivery_outcome(
        cls,
        job_id: str,
        from_status: str,
        to_status: str,
    ) -> Optional[Dict[str, Any]]:
        """Atomically update status counters as individual deliveries transition."""
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        inc_map: Dict[str, int] = {}
        if from_status in ("queued", "sending"):
            inc_map[from_status] = -1
        if to_status in ("sending", "sent", "delivered", "failed", "bounced"):
            inc_map[to_status] = 1

        if not inc_map:
            return await cls.get_by_id(job_id)

        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": jid},
            {
                "$inc": inc_map,
                "$set": {"updated_at": now},
            },
            return_document=ReturnDocument.AFTER,
        )

        # Check if job is completed
        if doc:
            total = doc.get("total", 0)
            sent = doc.get("sent", 0)
            failed = doc.get("failed", 0)
            bounced = doc.get("bounced", 0)
            if (sent + failed + bounced) >= total and doc.get("status") == "processing":
                final_status = "completed_with_errors" if (failed > 0 or bounced > 0) else "completed"
                doc = await cls._collection().find_one_and_update(
                    {"_id": jid},
                    {
                        "$set": {
                            "status": final_status,
                            "completed_at": now,
                            "updated_at": now,
                        }
                    },
                    return_document=ReturnDocument.AFTER,
                )

        return cls._serialize(doc) if doc else None
