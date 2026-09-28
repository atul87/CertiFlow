from __future__ import annotations
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager


class AchievementRepository:
    COLLECTION_NAME = "achievements"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def create(
        cls,
        organization_id: str,
        name: str,
        description: str,
        criteria: str,
        skills: Optional[List[str]] = None,
        category: str = "certification",
        level: Optional[str] = None,
        image: Optional[str] = None,
        url: Optional[str] = None,
        credits: Optional[float] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        achievement_id = f"ach_{secrets.token_hex(8)}"
        doc = {
            "organization_id": str(organization_id),
            "achievement_id": achievement_id,
            "name": name.strip(),
            "description": description.strip(),
            "criteria": criteria.strip(),
            "skills": skills or [],
            "category": category,
            "level": level,
            "image": image,
            "url": url,
            "credits": credits,
            "created_at": now,
            "updated_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["id"] = str(res.inserted_id)
        if "_id" in doc:
            del doc["_id"]
        return doc

    @classmethod
    async def get_by_id(cls, identifier: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {
            "$or": [
                {"achievement_id": identifier},
                {"_id": ObjectId(identifier) if ObjectId.is_valid(identifier) else identifier}
            ]
        }
        if organization_id:
            query["organization_id"] = str(organization_id)

        doc = await cls._collection().find_one(query)
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def list_by_org(
        cls,
        organization_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = {"organization_id": str(organization_id)}
        total = await cls._collection().count_documents(query)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        for it in items:
            it["id"] = str(it.pop("_id"))
        return items, total

    @classmethod
    async def update(cls, identifier: str, organization_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {
            "$or": [
                {"achievement_id": identifier},
                {"_id": ObjectId(identifier) if ObjectId.is_valid(identifier) else identifier}
            ],
            "organization_id": str(organization_id)
        }
        updates["updated_at"] = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(query, {"$set": updates}, return_document=True)
        if not res:
            return None
        res["id"] = str(res.pop("_id"))
        return res

    @classmethod
    async def delete(cls, identifier: str, organization_id: str) -> bool:
        query: Dict[str, Any] = {
            "$or": [
                {"achievement_id": identifier},
                {"_id": ObjectId(identifier) if ObjectId.is_valid(identifier) else identifier}
            ],
            "organization_id": str(organization_id)
        }
        res = await cls._collection().delete_one(query)
        return res.deleted_count > 0
