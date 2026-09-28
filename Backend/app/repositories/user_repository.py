from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from app.core.database import DatabaseManager


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convert MongoDB _id to id string."""
    if not doc:
        return None
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    elif "id" not in d:
        d["id"] = str(d.get("import_id", ""))
    return d


class UserRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("users")

    @classmethod
    async def create(cls, email: str, password_hash: str, name: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "email": email.lower().strip(),
            "password_hash": password_hash,
            "name": name.strip(),
            "is_active": True,
            "email_verified": False,
            "created_at": now,
            "updated_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    @classmethod
    async def get_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": oid})
        return serialize_doc(doc)

    @classmethod
    async def get_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"email": email.lower().strip()})
        return serialize_doc(doc)

    @classmethod
    async def update(cls, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {"_id": oid},
            {"$set": updates},
            return_document=True
        )
        return serialize_doc(res)
