from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class EmailEventRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("email_events")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if doc.get("delivery_id"):
            s["delivery_id"] = str(doc["delivery_id"])
        return s

    @classmethod
    async def log_event(
        cls,
        delivery_id: str,
        event_type: str,
        provider: str,
        provider_event_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Log an email event idempotently.
        If provider_event_id is provided and already exists, returns (existing_doc, False).
        Otherwise inserts and returns (new_doc, True).
        """
        if provider_event_id:
            existing = await cls._collection().find_one({"provider_event_id": provider_event_id})
            if existing:
                return cls._serialize(existing), False

        now = timestamp or datetime.now(timezone.utc)
        doc = {
            "delivery_id": ObjectId(delivery_id),
            "provider": provider,
            "event_type": event_type,
            "timestamp": now,
            "metadata": metadata or {},
        }
        if provider_event_id:
            doc["provider_event_id"] = str(provider_event_id)
        try:
            res = await cls._collection().insert_one(doc)
            doc["_id"] = res.inserted_id
            return cls._serialize(doc), True
        except DuplicateKeyError:
            if provider_event_id:
                existing = await cls._collection().find_one({"provider_event_id": provider_event_id})
                if existing:
                    return cls._serialize(existing), False
            raise

    @classmethod
    async def get_events_for_delivery(cls, delivery_id: str) -> List[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return []
        cursor = cls._collection().find({"delivery_id": did}).sort("timestamp", 1)
        items = await cursor.to_list(length=100)
        return [cls._serialize(d) for d in items]
