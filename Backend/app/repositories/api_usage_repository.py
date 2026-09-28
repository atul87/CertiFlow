"""
Repository for api_usage_events collection (P8).
Records operational API request telemetry and computes usage metrics.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.core.database import DatabaseManager


class APIUsageRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("api_usage_events")

    @classmethod
    async def record_request(
        cls,
        org_id: str,
        api_key_id: Optional[str],
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        try:
            oid = ObjectId(org_id)
            kid = ObjectId(api_key_id) if api_key_id else None
        except Exception:
            return

        doc = {
            "organization_id": oid,
            "api_key_id": kid,
            "method": method.upper(),
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "created_at": datetime.now(timezone.utc),
        }
        try:
            await cls._collection().insert_one(doc)
        except Exception:
            pass

    @classmethod
    async def get_metrics(
        cls,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "total_requests": 0, "successful_2xx": 0, "client_errors_4xx": 0,
                "server_errors_5xx": 0, "rate_limited_429": 0, "average_latency_ms": 0.0,
                "by_key": [], "by_endpoint": []
            }

        match = {"organization_id": oid, "created_at": {"$gte": start_date, "$lte": end_date}}

        # Aggregate totals and status categories
        pipeline = [
            {"$match": match},
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "c_2xx": {"$sum": {"$cond": [{"$and": [{"$gte": ["$status_code", 200]}, {"$lt": ["$status_code", 300]}]}, 1, 0]}},
                    "c_4xx": {"$sum": {"$cond": [{"$and": [{"$gte": ["$status_code", 400]}, {"$lt": ["$status_code", 500]}, {"$ne": ["$status_code", 429]}]}, 1, 0]}},
                    "c_5xx": {"$sum": {"$cond": [{"$gte": ["$status_code", 500]}, 1, 0]}},
                    "c_429": {"$sum": {"$cond": [{"$eq": ["$status_code", 429]}, 1, 0]}},
                    "avg_lat": {"$avg": "$duration_ms"},
                }
            }
        ]
        results = await cls._collection().aggregate(pipeline).to_list(length=1)
        r = results[0] if results else {}

        # Breakdown by endpoint
        ep_pipeline = [
            {"$match": match},
            {"$group": {"_id": {"method": "$method", "path": "$path"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        ep_raw = await cls._collection().aggregate(ep_pipeline).to_list(length=10)
        by_endpoint = [
            {"method": item["_id"]["method"], "path": item["_id"]["path"], "count": item["count"]}
            for item in ep_raw
        ]

        return {
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "total_requests": r.get("total", 0),
            "successful_2xx": r.get("c_2xx", 0),
            "client_errors_4xx": r.get("c_4xx", 0),
            "server_errors_5xx": r.get("c_5xx", 0),
            "rate_limited_429": r.get("c_429", 0),
            "average_latency_ms": round(r.get("avg_lat", 0.0), 1) if r.get("avg_lat") else 0.0,
            "by_key": [],
            "by_endpoint": by_endpoint,
        }
