from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class AnalyticsDailyRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("analytics_daily")

    @classmethod
    async def upsert_daily(
        cls,
        organization_id: str,
        date_str: str,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        oid = ObjectId(organization_id)
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"organization_id": oid, "date": date_str},
            {
                "$set": {
                    **metrics,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "organization_id": oid,
                    "date": date_str,
                    "created_at": now,
                }
            },
            upsert=True,
            return_document=True,
        )
        return serialize_doc(doc)

    @classmethod
    async def get_daily(
        cls,
        organization_id: str,
        date_str: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"organization_id": oid, "date": date_str})
        return serialize_doc(doc) if doc else None

    @classmethod
    async def get_daily_range(
        cls,
        organization_id: str,
        start_date_str: str,
        end_date_str: str,
    ) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return []
        cursor = cls._collection().find({
            "organization_id": oid,
            "date": {"$gte": start_date_str, "$lte": end_date_str}
        }).sort("date", 1)
        items = await cursor.to_list(length=365)
        return [serialize_doc(d) for d in items]
