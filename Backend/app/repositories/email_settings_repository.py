from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from app.core.config import settings
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class EmailSettingsRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("email_settings")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        s["organization_id"] = str(doc.get("organization_id", ""))
        return s

    @classmethod
    async def get_by_org(cls, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"organization_id": oid})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def upsert(
        cls,
        organization_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            raise ValueError(f"Invalid organization_id: {organization_id}")

        now = datetime.now(timezone.utc)
        updates["updated_at"] = now
        # Clean None values if desired, or keep them
        set_data = {k: v for k, v in updates.items() if v is not None}
        set_data["updated_at"] = now

        doc = await cls._collection().find_one_and_update(
            {"organization_id": oid},
            {"$set": set_data, "$setOnInsert": {"organization_id": oid}},
            upsert=True,
            return_document=True,
        )
        return cls._serialize(doc)

    @classmethod
    def to_safe_response(cls, doc: Optional[Dict[str, Any]], organization_id: str) -> Dict[str, Any]:
        """Returns email settings response with secrets masked/boolean flags."""
        if not doc:
            return {
                "organization_id": organization_id,
                "provider": settings.EMAIL_PROVIDER,
                "sender_name": settings.DEFAULT_SENDER_NAME,
                "sender_email": settings.DEFAULT_SENDER_EMAIL,
                "reply_to": None,
                "smtp_host": None,
                "smtp_port": None,
                "smtp_username": None,
                "has_smtp_password": False,
                "has_api_key": False,
                "auto_email_on_issuance": False,
                "updated_at": None,
            }

        return {
            "organization_id": str(doc.get("organization_id", organization_id)),
            "provider": doc.get("provider", settings.EMAIL_PROVIDER),
            "sender_name": doc.get("sender_name", settings.DEFAULT_SENDER_NAME),
            "sender_email": doc.get("sender_email", settings.DEFAULT_SENDER_EMAIL),
            "reply_to": doc.get("reply_to"),
            "smtp_host": doc.get("smtp_host"),
            "smtp_port": doc.get("smtp_port"),
            "smtp_username": doc.get("smtp_username"),
            "has_smtp_password": bool(doc.get("smtp_password")),
            "has_api_key": bool(doc.get("api_key")),
            "auto_email_on_issuance": bool(doc.get("auto_email_on_issuance", False)),
            "updated_at": doc.get("updated_at"),
        }
