from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
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
        res_oid = None

        if resource_id:
            try:
                res_oid = ObjectId(resource_id)
            except Exception:
                res_oid = resource_id

        doc = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": res_oid,
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
        return results

    @classmethod
    async def list_activity(
        cls,
        organization_id: str,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0

        query: Dict[str, Any] = {"organization_id": oid}
        if action:
            query["action"] = action
        if resource_type:
            query["resource_type"] = resource_type
        if user_id:
            try:
                query["user_id"] = ObjectId(user_id)
            except Exception:
                return [], 0
        if start_date and end_date:
            query["created_at"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["created_at"] = {"$gte": start_date}
        elif end_date:
            query["created_at"] = {"$lte": end_date}

        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
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
        return results, total
