from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from app.core.database import DatabaseManager


class UsageEventRepository:
    COLLECTION_NAME = "usage_events"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def record_event(
        cls,
        organization_id: str,
        metric: str,
        quantity: int,
        period: str,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Insert immutable usage audit event."""
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": str(organization_id),
            "metric": metric,
            "quantity": quantity,
            "period": period,
            "resource_id": str(resource_id) if resource_id else None,
            "metadata": metadata or {},
            "created_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["id"] = str(res.inserted_id)
        return doc

    @classmethod
    async def count_total_events(cls) -> int:
        """Count total platform usage events for admin reporting."""
        return await cls._collection().count_documents({})
