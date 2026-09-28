from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager


class SubscriptionRepository:
    COLLECTION_NAME = "subscriptions"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def get_by_org_id(cls, org_id: str) -> Optional[Dict[str, Any]]:
        """Fetch active subscription document for organization."""
        doc = await cls._collection().find_one({"organization_id": str(org_id)})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def get_by_provider_subscription_id(cls, provider_subscription_id: str) -> Optional[Dict[str, Any]]:
        """Lookup subscription by external billing provider subscription identifier."""
        doc = await cls._collection().find_one({"provider_subscription_id": provider_subscription_id})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def upsert_subscription(
        cls,
        organization_id: Optional[str] = None,
        plan_id: str = "free",
        status: str = "active",
        billing_interval: str = "monthly",
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        trial_ends_at: Optional[datetime] = None,
        provider: str = "mock",
        provider_subscription_id: Optional[str] = None,
        cancel_at_period_end: bool = False,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update subscription document for an organization."""
        target_org = str(organization_id or org_id)
        now = datetime.now(timezone.utc)
        start = current_period_start or now
        doc = {
            "organization_id": target_org,
            "plan_id": plan_id.lower(),
            "status": status.lower(),
            "billing_interval": billing_interval,
            "current_period_start": start,
            "current_period_end": current_period_end or now,
            "trial_ends_at": trial_ends_at,
            "provider": provider,
            "provider_subscription_id": provider_subscription_id,
            "cancel_at_period_end": cancel_at_period_end,
            "updated_at": now
        }
        res = await cls._collection().find_one_and_update(
            {"organization_id": target_org},
            {
                "$set": doc,
                "$setOnInsert": {"created_at": now}
            },
            upsert=True,
            return_document=True
        )
        res["id"] = str(res.pop("_id"))
        return res

    @classmethod
    async def update_status(
        cls,
        organization_id: str,
        status: str,
        cancel_at_period_end: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Update subscription state."""
        now = datetime.now(timezone.utc)
        updates: Dict[str, Any] = {"status": status.lower(), "updated_at": now}
        if cancel_at_period_end is not None:
            updates["cancel_at_period_end"] = cancel_at_period_end
            if cancel_at_period_end:
                updates["cancelled_at"] = now

        res = await cls._collection().find_one_and_update(
            {"organization_id": str(organization_id)},
            {"$set": updates},
            return_document=True
        )
        if not res:
            return None
        res["id"] = str(res.pop("_id"))
        return res

    @classmethod
    async def list_all(cls, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List subscriptions across platform for admin overview."""
        cursor = cls._collection().find({}).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        for doc in items:
            doc["id"] = str(doc.pop("_id"))
        return items
