from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.core.database import DatabaseManager


class BillingCustomerRepository:
    COLLECTION_NAME = "billing_customers"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def get_by_org_id(cls, org_id: str) -> Optional[Dict[str, Any]]:
        """Fetch billing customer profile for an organization."""
        doc = await cls._collection().find_one({"organization_id": str(org_id)})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def get_by_provider_customer_id(cls, provider: str, provider_customer_id: str) -> Optional[Dict[str, Any]]:
        """Find customer record by provider identifier."""
        doc = await cls._collection().find_one({
            "provider": provider,
            "provider_customer_id": provider_customer_id
        })
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def upsert_customer(
        cls,
        organization_id: str,
        provider: str,
        provider_customer_id: str,
        email: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save or update customer link to external billing system."""
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": str(organization_id),
            "provider": provider,
            "provider_customer_id": provider_customer_id,
            "email": email.lower().strip(),
            "name": name,
            "updated_at": now
        }
        res = await cls._collection().find_one_and_update(
            {"organization_id": str(organization_id)},
            {
                "$set": doc,
                "$setOnInsert": {"created_at": now}
            },
            upsert=True,
            return_document=True
        )
        res["id"] = str(res.pop("_id"))
        return res
