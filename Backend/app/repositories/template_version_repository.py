from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class TemplateVersionRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("template_versions")

    @classmethod
    async def get_next_version_number(cls, template_id: str) -> int:
        try:
            tid = ObjectId(template_id)
        except Exception:
            return 1
        latest = await cls._collection().find_one(
            {"template_id": tid},
            sort=[("version", -1)]
        )
        if latest and "version" in latest:
            return latest["version"] + 1
        return 1

    @classmethod
    async def create_version(
        cls,
        template_id: str,
        organization_id: str,
        created_by: str,
        design_type: str = "image",
        width: int = 3508,
        height: int = 2480,
        orientation: str = "landscape",
        background_asset_id: Optional[str] = None,
        elements: Optional[List[Dict[str, Any]]] = None,
        fields: Optional[List[Dict[str, Any]]] = None,
        status: str = "draft"
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        version_num = await cls.get_next_version_number(template_id)

        doc = {
            "template_id": ObjectId(template_id),
            "organization_id": ObjectId(organization_id),
            "version": version_num,
            "status": status,  # draft, published, archived
            "design_type": design_type,
            "width": width,
            "height": height,
            "orientation": orientation,
            "background_asset_id": ObjectId(background_asset_id) if background_asset_id else None,
            "elements": elements or [],
            "fields": fields or [],
            "created_by": ObjectId(created_by),
            "created_at": now,
            "updated_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        s["template_id"] = str(doc["template_id"])
        s["organization_id"] = str(doc["organization_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("background_asset_id"):
            s["background_asset_id"] = str(doc["background_asset_id"])
        return s

    @classmethod
    async def get_by_id(cls, version_id: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            vid = ObjectId(version_id)
        except Exception:
            return None

        query: Dict[str, Any] = {"_id": vid}
        if organization_id:
            query["organization_id"] = ObjectId(organization_id)

        doc = await cls._collection().find_one(query)
        if not doc:
            return None
        s = serialize_doc(doc)
        s["template_id"] = str(doc["template_id"])
        s["organization_id"] = str(doc["organization_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("background_asset_id"):
            s["background_asset_id"] = str(doc["background_asset_id"])
        return s

    @classmethod
    async def get_latest_version(cls, template_id: str) -> Optional[Dict[str, Any]]:
        try:
            tid = ObjectId(template_id)
        except Exception:
            return None

        doc = await cls._collection().find_one(
            {"template_id": tid},
            sort=[("version", -1)]
        )
        if not doc:
            return None
        s = serialize_doc(doc)
        s["template_id"] = str(doc["template_id"])
        s["organization_id"] = str(doc["organization_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("background_asset_id"):
            s["background_asset_id"] = str(doc["background_asset_id"])
        return s

    @classmethod
    async def list_by_template(cls, template_id: str, organization_id: str) -> List[Dict[str, Any]]:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return []

        cursor = cls._collection().find({"template_id": tid, "organization_id": oid}).sort("version", -1)
        items = await cursor.to_list(length=50)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["template_id"] = str(doc["template_id"])
            s["organization_id"] = str(doc["organization_id"])
            s["created_by"] = str(doc["created_by"])
            if doc.get("background_asset_id"):
                s["background_asset_id"] = str(doc["background_asset_id"])
            results.append(s)
        return results

    @classmethod
    async def update_version(
        cls,
        version_id: str,
        organization_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            vid = ObjectId(version_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        # Convert background_asset_id to ObjectId if passed
        if "background_asset_id" in updates and updates["background_asset_id"]:
            try:
                updates["background_asset_id"] = ObjectId(updates["background_asset_id"])
            except Exception:
                pass

        updates["updated_at"] = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {"_id": vid, "organization_id": oid, "status": "draft"},  # Only draft versions can be modified!
            {"$set": updates},
            return_document=True
        )
        if not res:
            return None
        s = serialize_doc(res)
        s["template_id"] = str(res["template_id"])
        s["organization_id"] = str(res["organization_id"])
        s["created_by"] = str(res["created_by"])
        if res.get("background_asset_id"):
            s["background_asset_id"] = str(res["background_asset_id"])
        return s

    @classmethod
    async def publish_version(cls, version_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            vid = ObjectId(version_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        now = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {"_id": vid, "organization_id": oid},
            {"$set": {"status": "published", "updated_at": now}},
            return_document=True
        )
        if not res:
            return None
        s = serialize_doc(res)
        s["template_id"] = str(res["template_id"])
        s["organization_id"] = str(res["organization_id"])
        s["created_by"] = str(res["created_by"])
        if res.get("background_asset_id"):
            s["background_asset_id"] = str(res["background_asset_id"])
        return s
