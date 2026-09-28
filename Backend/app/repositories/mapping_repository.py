from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class MappingRepository:
    @staticmethod
    def _mapping_collection():
        return DatabaseManager.get_collection("import_mappings")

    @staticmethod
    def _profile_collection():
        return DatabaseManager.get_collection("mapping_profiles")

    @classmethod
    async def save_mapping(
        cls,
        import_id: str,
        template_version_id: Optional[str],
        organization_id: str,
        mappings: List[Dict[str, Any]],
        confirmed_by: str
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        iid = ObjectId(import_id)
        oid = ObjectId(organization_id)
        vid = ObjectId(template_version_id) if template_version_id else None

        doc = {
            "import_id": iid,
            "template_version_id": vid,
            "organization_id": oid,
            "mappings": mappings,
            "confirmed_by": ObjectId(confirmed_by),
            "confirmed_at": now
        }

        await cls._mapping_collection().update_one(
            {"import_id": iid},
            {"$set": doc},
            upsert=True
        )

        saved = await cls._mapping_collection().find_one({"import_id": iid})
        target_doc = saved if saved else doc
        s = serialize_doc(target_doc)
        s["import_id"] = str(target_doc["import_id"])
        s["organization_id"] = str(target_doc["organization_id"])
        s["confirmed_by"] = str(target_doc["confirmed_by"])
        if target_doc.get("template_version_id"):
            s["template_version_id"] = str(target_doc["template_version_id"])
        return s

    @classmethod
    async def get_mapping(cls, import_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(import_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        doc = await cls._mapping_collection().find_one({"import_id": iid, "organization_id": oid})
        if not doc:
            return None
        s = serialize_doc(doc)
        s["import_id"] = str(doc["import_id"])
        s["organization_id"] = str(doc["organization_id"])
        s["confirmed_by"] = str(doc["confirmed_by"])
        if doc.get("template_version_id"):
            s["template_version_id"] = str(doc["template_version_id"])
        return s

    # Profiles
    @classmethod
    async def create_profile(
        cls,
        organization_id: str,
        name: str,
        mappings: List[Dict[str, Any]],
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "template_id": ObjectId(template_id) if template_id else None,
            "name": name.strip(),
            "mappings": mappings,
            "created_at": now,
            "updated_at": now
        }
        res = await cls._profile_collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        if doc.get("template_id"):
            s["template_id"] = str(doc["template_id"])
        return s

    @classmethod
    async def list_profiles(cls, organization_id: str, template_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return []

        query: Dict[str, Any] = {"organization_id": oid}
        if template_id:
            try:
                query["template_id"] = ObjectId(template_id)
            except Exception:
                pass

        cursor = cls._profile_collection().find(query).sort("name", 1)
        items = await cursor.to_list(length=100)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["organization_id"] = str(doc["organization_id"])
            if doc.get("template_id"):
                s["template_id"] = str(doc["template_id"])
            results.append(s)
        return results

    @classmethod
    async def delete_profile(cls, profile_id: str, organization_id: str) -> bool:
        try:
            pid = ObjectId(profile_id)
            oid = ObjectId(organization_id)
        except Exception:
            return False

        res = await cls._profile_collection().delete_one({"_id": pid, "organization_id": oid})
        return res.deleted_count > 0
