from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.core.database import DatabaseManager

DEFAULT_PLANS: List[Dict[str, Any]] = [
    {
        "plan_id": "free",
        "name": "Free Community",
        "description": "Essential certificate generation for individuals and small test projects.",
        "price_monthly": 0,
        "price_yearly": 0,
        "currency": "INR",
        "entitlements": {
            "max_certificates_monthly": 100,
            "max_storage_bytes": 1073741824,  # 1 GB
            "max_templates": 3,
            "max_members": 2,
            "max_teams": 1,
            "max_webhooks": 0,
            "api_access": False,
            "custom_roles": False,
            "analytics_history_days": 30,
            "csv_max_rows": 500,
            "priority_worker_queue": False,
            "white_label_email": False,
        },
        "features": [
            "100 certificates per month",
            "1 GB asset storage",
            "Up to 3 templates",
            "Public verification & QR codes",
            "CSV bulk import (up to 500 rows)"
        ],
        "is_active": True,
        "provider_price_id_monthly": None,
        "provider_price_id_yearly": None
    },
    {
        "plan_id": "starter",
        "name": "Starter",
        "description": "Growing academies, bootcamps, and workshop organizers.",
        "price_monthly": 499,
        "price_yearly": 4990,
        "currency": "INR",
        "entitlements": {
            "max_certificates_monthly": 1000,
            "max_storage_bytes": 5368709120,  # 5 GB
            "max_templates": 10,
            "max_members": 5,
            "max_teams": 3,
            "max_webhooks": 2,
            "api_access": True,
            "custom_roles": False,
            "analytics_history_days": 90,
            "csv_max_rows": 2500,
            "priority_worker_queue": False,
            "white_label_email": False,
        },
        "features": [
            "1,000 certificates per month",
            "5 GB asset storage",
            "10 templates & 5 team seats",
            "Developer REST API & API keys",
            "Outbound Webhooks (2 endpoints)",
            "90 days analytics history"
        ],
        "is_active": True,
        "provider_price_id_monthly": "price_starter_monthly",
        "provider_price_id_yearly": "price_starter_yearly"
    },
    {
        "plan_id": "pro",
        "name": "Professional",
        "description": "Universities, accredited institutions, and large training organizations.",
        "price_monthly": 1999,
        "price_yearly": 19990,
        "currency": "INR",
        "entitlements": {
            "max_certificates_monthly": 5000,
            "max_storage_bytes": 26843545600,  # 25 GB
            "max_templates": 50,
            "max_members": 15,
            "max_teams": 10,
            "max_webhooks": 10,
            "api_access": True,
            "custom_roles": True,
            "analytics_history_days": 365,
            "csv_max_rows": 10000,
            "priority_worker_queue": True,
            "white_label_email": True,
        },
        "features": [
            "5,000 certificates per month",
            "25 GB asset storage",
            "50 templates & 15 team seats",
            "Granular custom RBAC roles",
            "Priority queue worker execution",
            "Custom white-label email sender",
            "10 Webhook endpoints",
            "Full 1-year analytics & audit history"
        ],
        "is_active": True,
        "provider_price_id_monthly": "price_pro_monthly",
        "provider_price_id_yearly": "price_pro_yearly"
    },
    {
        "plan_id": "business",
        "name": "Business Scale",
        "description": "National certifications, multi-department enterprise institutions.",
        "price_monthly": 4999,
        "price_yearly": 49990,
        "currency": "INR",
        "entitlements": {
            "max_certificates_monthly": 25000,
            "max_storage_bytes": 107374182400,  # 100 GB
            "max_templates": 200,
            "max_members": 50,
            "max_teams": 50,
            "max_webhooks": 50,
            "api_access": True,
            "custom_roles": True,
            "analytics_history_days": 730,
            "csv_max_rows": 50000,
            "priority_worker_queue": True,
            "white_label_email": True,
        },
        "features": [
            "25,000 certificates per month",
            "100 GB asset storage",
            "200 templates & 50 team seats",
            "50 Webhook subscriptions",
            "Dedicated high-speed worker pool",
            "2-year analytics & audit logs"
        ],
        "is_active": True,
        "provider_price_id_monthly": "price_business_monthly",
        "provider_price_id_yearly": "price_business_yearly"
    },
    {
        "plan_id": "enterprise",
        "name": "Enterprise Custom",
        "description": "Government bodies, global accreditation networks, unlimited scale.",
        "price_monthly": 14999,
        "price_yearly": 149990,
        "currency": "INR",
        "entitlements": {
            "max_certificates_monthly": 100000,
            "max_storage_bytes": 1099511627776,  # 1 TB
            "max_templates": 1000,
            "max_members": 500,
            "max_teams": 200,
            "max_webhooks": 200,
            "api_access": True,
            "custom_roles": True,
            "analytics_history_days": 1825,
            "csv_max_rows": 100000,
            "priority_worker_queue": True,
            "white_label_email": True,
        },
        "features": [
            "100,000+ certificates per month",
            "1 TB dedicated storage",
            "Custom contracts & SLA guarantee",
            "5-year compliance retention",
            "Dedicated technical account manager"
        ],
        "is_active": True,
        "provider_price_id_monthly": "price_enterprise_monthly",
        "provider_price_id_yearly": "price_enterprise_yearly"
    }
]


class PlanRepository:
    COLLECTION_NAME = "plans"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def ensure_default_plans(cls) -> None:
        """Seed default plans idempotently if not present."""
        for plan in DEFAULT_PLANS:
            await cls._collection().update_one(
                {"plan_id": plan["plan_id"]},
                {"$setOnInsert": plan},
                upsert=True
            )

    @classmethod
    async def get_by_id(cls, plan_id: str) -> Optional[Dict[str, Any]]:
        """Lookup plan by plan_id."""
        doc = await cls._collection().find_one({"plan_id": plan_id.lower()})
        if not doc:
            # Fallback to local default if DB has not been seeded yet
            for p in DEFAULT_PLANS:
                if p["plan_id"] == plan_id.lower():
                    return p
            return None
        doc["id"] = str(doc.get("_id", doc.get("plan_id")))
        return doc

    @classmethod
    async def list_active_plans(cls) -> List[Dict[str, Any]]:
        """List all active customer-facing plans."""
        cursor = cls._collection().find({"is_active": True})
        items = await cursor.to_list(length=50)
        if not items:
            return DEFAULT_PLANS
        for doc in items:
            doc["id"] = str(doc.get("_id", doc.get("plan_id")))
        return items
