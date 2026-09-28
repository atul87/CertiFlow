from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from app.core.database import DatabaseManager


class PasswordResetRepository:
    COLLECTION_NAME = "password_reset_tokens"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def create_token(
        cls,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Insert a new single-use password reset token record."""
        now = datetime.now(timezone.utc)
        doc = {
            "user_id": user_id,
            "token_hash": token_hash,
            "created_at": now,
            "expires_at": expires_at,
            "used_at": None,
            "ip_address": ip_address
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    @classmethod
    async def find_valid_token(cls, token_hash: str) -> Optional[Dict[str, Any]]:
        """Find an unexpired, unused token by its SHA-256 hash."""
        now = datetime.now(timezone.utc)
        return await cls._collection().find_one({
            "token_hash": token_hash,
            "used_at": None,
            "expires_at": {"$gt": now}
        })

    @classmethod
    async def mark_used(cls, token_hash: str) -> bool:
        """Mark a token as consumed."""
        now = datetime.now(timezone.utc)
        res = await cls._collection().update_one(
            {"token_hash": token_hash},
            {"$set": {"used_at": now}}
        )
        return res.modified_count > 0

    @classmethod
    async def invalidate_all_for_user(cls, user_id: str) -> int:
        """Invalidate all active reset tokens for a given user."""
        now = datetime.now(timezone.utc)
        res = await cls._collection().update_many(
            {"user_id": user_id, "used_at": None},
            {"$set": {"used_at": now}}
        )
        return res.modified_count
