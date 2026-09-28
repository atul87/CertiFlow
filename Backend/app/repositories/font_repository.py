from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc

DEFAULT_SYSTEM_FONTS = [
    {"name": "Inter", "family": "Inter", "source": "system", "organization_id": None},
    {"name": "Poppins", "family": "Poppins", "source": "system", "organization_id": None},
    {"name": "Montserrat", "family": "Montserrat", "source": "system", "organization_id": None},
    {"name": "Roboto", "family": "Roboto", "source": "system", "organization_id": None},
    {"name": "Open Sans", "family": "Open Sans", "source": "system", "organization_id": None},
    {"name": "Playfair Display", "family": "Playfair Display", "source": "system", "organization_id": None},
    {"name": "Lora", "family": "Lora", "source": "system", "organization_id": None},
]


class FontRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("fonts")

    @classmethod
    async def list_available_fonts(cls, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        # Ensure system fonts exist in collection
        sys_count = await cls._collection().count_documents({"source": "system"})
        if sys_count == 0:
            await cls._collection().insert_many(DEFAULT_SYSTEM_FONTS)

        query: Dict[str, Any] = {"$or": [{"source": "system"}]}
        if organization_id:
            try:
                oid = ObjectId(organization_id)
                query["$or"].append({"organization_id": oid})
            except Exception:
                pass

        cursor = cls._collection().find(query).sort("name", 1)
        items = await cursor.to_list(length=100)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            if doc.get("organization_id"):
                s["organization_id"] = str(doc["organization_id"])
            results.append(s)
        return results

    @classmethod
    async def create_custom_font(
        cls,
        name: str,
        family: str,
        organization_id: str,
        storage_key: Optional[str] = None
    ) -> Dict[str, Any]:
        doc = {
            "name": name.strip(),
            "family": family.strip(),
            "source": "custom",
            "organization_id": ObjectId(organization_id),
            "storage_key": storage_key
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        return s
