from __future__ import annotations
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager
from app.core.config import settings


class IssuerRepository:
    COLLECTION_NAME = "issuer_profiles"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def get_by_org_id(cls, organization_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"organization_id": str(organization_id)})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def get_by_issuer_id(cls, issuer_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"issuer_id": issuer_id})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def create(
        cls,
        organization_id: str,
        name: str,
        description: Optional[str] = None,
        logo: Optional[str] = None,
        website: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        active_key_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        issuer_id = f"iss_{secrets.token_hex(8)}"
        base_url = settings.APP_BASE_URL.rstrip("/")
        issuer_url = f"{base_url}/api/v1/public/issuers/{issuer_id}"
        verification_url = f"{base_url}/api/v1/public/credentials"

        doc = {
            "organization_id": str(organization_id),
            "issuer_id": issuer_id,
            "name": name.strip(),
            "description": description,
            "logo": logo,
            "website": website,
            "email": email,
            "phone": phone,
            "address": address,
            "issuer_url": issuer_url,
            "verification_url": verification_url,
            "status": "active",
            "active_key_id": active_key_id,
            "created_at": now,
            "updated_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["id"] = str(res.inserted_id)
        if "_id" in doc:
            del doc["_id"]
        return doc

    @classmethod
    async def update(cls, organization_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = datetime.now(timezone.utc)
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
    async def set_active_key(cls, organization_id: str, key_id: str) -> None:
        await cls._collection().update_one(
            {"organization_id": str(organization_id)},
            {"$set": {"active_key_id": key_id, "updated_at": datetime.now(timezone.utc)}}
        )
