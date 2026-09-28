from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.core.database import DatabaseManager


class EntitlementOverrideRepository:
    COLLECTION_NAME = "entitlement_overrides"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def grant_override(
        cls,
        organization_id: Optional[str] = None,
        feature: Optional[str] = None,
        quantity: int = 1,
        reason: str = "Admin override",
        created_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        org_id: Optional[str] = None,
        metric: Optional[str] = None,
        granted_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Grant a temporary or promotional quota override to an organization."""
        target_org = str(organization_id or org_id)
        target_feature = str(feature or metric)
        target_user = str(created_by or granted_by) if (created_by or granted_by) else None
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": target_org,
            "feature": target_feature,
            "quantity": quantity,
            "reason": reason,
            "created_by": target_user,
            "expires_at": expires_at,
            "created_at": now
        }
        res = await cls._collection().update_one(
            {"organization_id": target_org, "feature": target_feature},
            {"$set": doc},
            upsert=True
        )
        return doc

    @classmethod
    async def get_active_overrides(cls, organization_id: str) -> Dict[str, int]:
        """Fetch all unexpired quota overrides for organization."""
        now = datetime.now(timezone.utc)
        cursor = cls._collection().find({
            "organization_id": str(organization_id),
            "$or": [
                {"expires_at": None},
                {"expires_at": {"$gt": now}}
            ]
        })
        items = await cursor.to_list(length=50)
        overrides = {}
        for item in items:
            overrides[item["feature"]] = int(item.get("quantity", 0))
        return overrides
