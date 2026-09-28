from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from pymongo import ReturnDocument

from app.core.database import DatabaseManager
from app.core.config import settings
from app.repositories.user_repository import serialize_doc


class ReportJobRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("report_jobs")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        for field in ("organization_id", "created_by"):
            if doc.get(field):
                s[field] = str(doc[field])
        return s

    @classmethod
    async def create(
        cls,
        organization_id: str,
        report_type: str,
        format_type: str,
        filters: Dict[str, Any],
        created_by: str,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=settings.REPORT_EXPIRY_HOURS)

        doc = {
            "organization_id": ObjectId(organization_id),
            "type": report_type,
            "format": format_type,
            "status": "queued",
            "filters": filters or {},
            "storage_key": None,
            "row_count": 0,
            "file_size_bytes": 0,
            "error": None,
            "created_by": ObjectId(created_by),
            "created_at": now,
            "completed_at": None,
            "expires_at": expires_at,
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
        storage_key: Optional[str] = None,
        row_count: int = 0,
        file_size_bytes: int = 0,
        error: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        now = datetime.now(timezone.utc)
        updates: Dict[str, Any] = {"status": status}
        if status in ("completed", "failed", "cancelled"):
            updates["completed_at"] = now
        if storage_key:
            updates["storage_key"] = storage_key
        if row_count > 0:
            updates["row_count"] = row_count
        if file_size_bytes > 0:
            updates["file_size_bytes"] = file_size_bytes
        if error:
            updates["error"] = error

        doc = await cls._collection().find_one_and_update(
            {"_id": jid},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None
