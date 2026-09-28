from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pymongo import ReturnDocument
from app.core.database import DatabaseManager


class UsageCounterRepository:
    COLLECTION_NAME = "usage_counters"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def increment_counter(
        cls,
        organization_id: str,
        metric: str,
        period: str,
        quantity: int = 1
    ) -> int:
        """
        Atomically increment usage counter for organization, metric, and billing period.
        Returns the updated counter value.
        """
        now = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {
                "organization_id": str(organization_id),
                "metric": metric,
                "period": period
            },
            {
                "$inc": {"quantity": quantity},
                "$set": {"updated_at": now},
                "$setOnInsert": {"created_at": now}
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return int(res.get("quantity", 0))

    @classmethod
    async def set_gauge(
        cls,
        organization_id: Optional[str] = None,
        metric: str = "certificates_generated",
        period: str = "",
        quantity: int = 0,
        org_id: Optional[str] = None
    ) -> int:
        """Set absolute value for gauge metrics such as current storage bytes."""
        target_org = str(organization_id or org_id)
        now = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {
                "organization_id": target_org,
                "metric": metric,
                "period": period
            },
            {
                "$set": {"quantity": quantity, "updated_at": now},
                "$setOnInsert": {"created_at": now}
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return int(res.get("quantity", 0))

    set_counter = set_gauge

    @classmethod
    async def get_counter(
        cls,
        organization_id: str,
        metric: str,
        period: str
    ) -> int:
        """Fetch current value of a usage metric."""
        doc = await cls._collection().find_one({
            "organization_id": str(organization_id),
            "metric": metric,
            "period": period
        })
        return int(doc["quantity"]) if doc else 0

    @classmethod
    async def get_all_for_period(
        cls,
        organization_id: str,
        period: str
    ) -> Dict[str, int]:
        """Fetch all metric counters for organization in given period."""
        cursor = cls._collection().find({
            "organization_id": str(organization_id),
            "period": period
        })
        items = await cursor.to_list(length=100)
        return {item["metric"]: int(item.get("quantity", 0)) for item in items}
