from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class RefreshTokenRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("refresh_tokens")

    @classmethod
    async def create(
        cls,
        user_id: str,
        organization_id: Optional[str],
        token_hash: str,
        expires_at: datetime
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "user_id": ObjectId(user_id),
            "organization_id": ObjectId(organization_id) if organization_id else None,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "created_at": now,
            "revoked": False
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        s["user_id"] = str(doc["user_id"])
        s["organization_id"] = str(doc["organization_id"]) if doc["organization_id"] else None
        return s

    @classmethod
    async def find_valid(cls, token_hash: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one({
            "token_hash": token_hash,
            "revoked": False,
            "expires_at": {"$gt": now}
        })
        if not doc:
            return None
        s = serialize_doc(doc)
        s["user_id"] = str(doc["user_id"])
        s["organization_id"] = str(doc["organization_id"]) if doc["organization_id"] else None
        return s

    @classmethod
    async def revoke(cls, token_hash: str) -> bool:
        res = await cls._collection().update_one(
            {"token_hash": token_hash},
            {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc)}}
        )
        return res.modified_count > 0

    @classmethod
    async def revoke_all_for_user(cls, user_id: str) -> int:
        try:
            uid = ObjectId(user_id)
        except Exception:
            return 0
        res = await cls._collection().update_many(
            {"user_id": uid, "revoked": False},
            {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc)}}
        )
        return res.modified_count
