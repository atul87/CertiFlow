from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class AssetRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("assets")

    @classmethod
    async def create(
        cls,
        organization_id: str,
        filename: str,
        mime_type: str,
        size: int,
        storage_key: str,
        asset_type: str,
        width: int,
        height: int,
        created_by: str,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "template_id": ObjectId(template_id) if template_id else None,
            "filename": filename,
            "mime_type": mime_type,
            "size": size,
            "storage_key": storage_key,
            "asset_type": asset_type,  # background, logo, signature, seal, watermark
            "width": width,
            "height": height,
            "created_by": ObjectId(created_by),
            "created_at": now,
            "deleted_at": None
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("template_id"):
            s["template_id"] = str(doc["template_id"])
        return s

    @classmethod
    async def get_by_id(cls, asset_id: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            aid = ObjectId(asset_id)
        except Exception:
            return None

        query: Dict[str, Any] = {"_id": aid, "deleted_at": None}
        if organization_id:
            query["organization_id"] = ObjectId(organization_id)

        doc = await cls._collection().find_one(query)
        if not doc:
            return None
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("template_id"):
            s["template_id"] = str(doc["template_id"])
        return s

    @classmethod
    async def list_by_template(cls, template_id: str, organization_id: str) -> List[Dict[str, Any]]:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return []

        cursor = cls._collection().find({
            "template_id": tid,
            "organization_id": oid,
            "deleted_at": None
        }).sort("created_at", -1)
        items = await cursor.to_list(length=100)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["organization_id"] = str(doc["organization_id"])
            s["created_by"] = str(doc["created_by"])
            if doc.get("template_id"):
                s["template_id"] = str(doc["template_id"])
            results.append(s)
        return results

    @classmethod
    async def delete(cls, asset_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            aid = ObjectId(asset_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        now = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {"_id": aid, "organization_id": oid, "deleted_at": None},
            {"$set": {"deleted_at": now}},
            return_document=True
        )
        if not res:
            return None
        s = serialize_doc(res)
        s["organization_id"] = str(res["organization_id"])
        s["created_by"] = str(res["created_by"])
        if res.get("template_id"):
            s["template_id"] = str(res["template_id"])
        return s
