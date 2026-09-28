import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


def slugify(text: str) -> str:
    """Generate a URL-safe lowercase slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "org"


class OrganizationRepository:
    @staticmethod
    def _org_collection():
        return DatabaseManager.get_collection("organizations")

    @staticmethod
    def _members_collection():
        return DatabaseManager.get_collection("organization_members")

    @classmethod
    async def create(cls, name: str, owner_id: str, slug: Optional[str] = None) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        base_slug = slugify(slug or name)

        # Ensure slug uniqueness
        unique_slug = base_slug
        counter = 1
        while await cls._org_collection().find_one({"slug": unique_slug}):
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        org_doc = {
            "name": name.strip(),
            "slug": unique_slug,
            "owner_id": ObjectId(owner_id),
            "plan": "free",
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        res = await cls._org_collection().insert_one(org_doc)
        org_doc["_id"] = res.inserted_id
        org_serialized = serialize_doc(org_doc)
        org_serialized["owner_id"] = str(org_doc["owner_id"])

        # Create owner membership automatically
        member_doc = {
            "organization_id": res.inserted_id,
            "user_id": ObjectId(owner_id),
            "role": "owner",
            "status": "active",
            "created_at": now
        }
        await cls._members_collection().insert_one(member_doc)

        return org_serialized

    @classmethod
    async def get_by_id(cls, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._org_collection().find_one({"_id": oid})
        if not doc:
            return None
        s = serialize_doc(doc)
        s["owner_id"] = str(doc["owner_id"])
        return s

    @classmethod
    async def get_by_slug(cls, slug: str) -> Optional[Dict[str, Any]]:
        doc = await cls._org_collection().find_one({"slug": slug})
        if not doc:
            return None
        s = serialize_doc(doc)
        s["owner_id"] = str(doc["owner_id"])
        return s

    @classmethod
    async def update(cls, org_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        res = await cls._org_collection().find_one_and_update(
            {"_id": oid},
            {"$set": updates},
            return_document=True
        )
        if not res:
            return None
        s = serialize_doc(res)
        s["owner_id"] = str(res["owner_id"])
        return s

    @classmethod
    async def get_user_membership(cls, org_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
            uid = ObjectId(user_id)
        except Exception:
            return None
        doc = await cls._members_collection().find_one({"organization_id": oid, "user_id": uid})
        if not doc:
            return None
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        s["user_id"] = str(doc["user_id"])
        return s

    @classmethod
    async def get_user_primary_organization(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user's primary/first organization and their membership."""
        try:
            uid = ObjectId(user_id)
        except Exception:
            return None
        membership = await cls._members_collection().find_one({"user_id": uid, "status": "active"})
        if not membership:
            return None
        org = await cls._org_collection().find_one({"_id": membership["organization_id"]})
        if not org:
            return None
        s = serialize_doc(org)
        s["owner_id"] = str(org["owner_id"])
        s["member_role"] = membership.get("role", "member")
        return s

    @classmethod
    async def list_members(cls, org_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []

        cursor = cls._members_collection().find({"organization_id": oid})
        members = await cursor.to_list(length=100)

        results = []
        user_col = DatabaseManager.get_collection("users")
        for m in members:
            sm = serialize_doc(m)
            sm["organization_id"] = str(m["organization_id"])
            sm["user_id"] = str(m["user_id"])

            # Attach user summary if available
            u = await user_col.find_one({"_id": m["user_id"]})
            if u:
                sm["user"] = {
                    "id": str(u["_id"]),
                    "name": u.get("name", ""),
                    "email": u.get("email", "")
                }
            results.append(sm)
        return results
