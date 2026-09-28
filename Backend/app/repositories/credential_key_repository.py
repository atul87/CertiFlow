from __future__ import annotations
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.core.database import DatabaseManager


class CredentialKeyRepository:
    COLLECTION_NAME = "credential_keys"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def create_key(
        cls,
        issuer_id: str,
        organization_id: str,
        algorithm: str,
        public_key_pem: str,
        encrypted_private_key: str,
        status: str = "active"
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        key_id = f"key_{algorithm.lower()}_{secrets.token_hex(6)}"
        doc = {
            "key_id": key_id,
            "issuer_id": issuer_id,
            "organization_id": str(organization_id),
            "algorithm": algorithm,
            "public_key": public_key_pem,
            "encrypted_private_key": encrypted_private_key,
            "status": status,
            "created_at": now,
            "activated_at": now,
            "retired_at": None
        }
        res = await cls._collection().insert_one(doc)
        doc["id"] = str(res.inserted_id)
        if "_id" in doc:
            del doc["_id"]
        return doc

    @classmethod
    async def get_active_key(cls, issuer_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"issuer_id": issuer_id, "status": "active"})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def get_key_by_id(cls, issuer_id: str, key_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"issuer_id": issuer_id, "key_id": key_id})
        if not doc:
            # Fallback search by key_id alone
            doc = await cls._collection().find_one({"key_id": key_id})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def list_public_keys(cls, issuer_id: str) -> List[Dict[str, Any]]:
        """List public key history for issuer (excluding encrypted private keys)."""
        cursor = cls._collection().find(
            {"issuer_id": issuer_id},
            {"encrypted_private_key": 0}
        ).sort("created_at", -1)
        items = await cursor.to_list(length=50)
        for it in items:
            it["id"] = str(it.pop("_id"))
        return items

    @classmethod
    async def retire_active_keys(cls, issuer_id: str) -> None:
        now = datetime.now(timezone.utc)
        await cls._collection().update_many(
            {"issuer_id": issuer_id, "status": "active"},
            {"$set": {"status": "retired", "retired_at": now}}
        )

    @classmethod
    async def mark_key_compromised(cls, key_id: str) -> None:
        now = datetime.now(timezone.utc)
        await cls._collection().update_one(
            {"key_id": key_id},
            {"$set": {"status": "compromised", "retired_at": now}}
        )
