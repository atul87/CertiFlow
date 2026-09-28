from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class AuditLogRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("audit_logs")

    @classmethod
    async def log_event(
        cls,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": ObjectId(resource_id) if resource_id else None,
            "organization_id": ObjectId(organization_id) if organization_id else None,
            "user_id": ObjectId(user_id) if user_id else None,
            "metadata": metadata or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        if s.get("resource_id"):
            s["resource_id"] = str(s["resource_id"])
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("user_id"):
            s["user_id"] = str(s["user_id"])
        return s

    @classmethod
    async def list_events(
        cls,
        organization_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return []
        cursor = cls._collection().find({"organization_id": oid}).sort("created_at", -1).limit(limit)
        events = await cursor.to_list(length=limit)
        results = []
        for e in events:
            s = serialize_doc(e)
            if s.get("resource_id"):
                s["resource_id"] = str(s["resource_id"])
            if s.get("organization_id"):
                s["organization_id"] = str(s["organization_id"])
            if s.get("user_id"):
                s["user_id"] = str(s["user_id"])
            results.append(s)
        return results
