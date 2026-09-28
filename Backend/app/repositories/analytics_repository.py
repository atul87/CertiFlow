from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from bson import ObjectId

from app.core.database import DatabaseManager
from app.core.config import settings
from app.repositories.user_repository import serialize_doc


class AnalyticsRepository:

    @classmethod
    async def get_kpis(cls, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Aggregate high-level KPIs for an organization in the given date range."""
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {
                "certificates_issued": 0,
                "active_certificates": 0,
                "revoked_certificates": 0,
                "emails_sent": 0,
                "emails_delivered": 0,
                "verifications_successful": 0,
                "failed_operations": 0,
            }

        db = DatabaseManager.get_db()
        date_query = {"$gte": start_date, "$lte": end_date}

        # 1. Certificates issued in period
        certs_issued = await db["certificates"].count_documents({
            "organization_id": oid,
            "created_at": date_query,
        })

        # 2. Currently active certificates (all time or created in period)
        active_certs = await db["certificates"].count_documents({
            "organization_id": oid,
            "status": {"$in": ["active", "generated"]},
        })

        # 3. Revoked certificates (in period)
        revoked_certs = await db["certificates"].count_documents({
            "organization_id": oid,
            "status": "revoked",
            "revoked_at": date_query,
        })

        # 4. Email delivery counts
        email_pipeline = [
            {"$match": {"organization_id": oid, "created_at": date_query}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        email_counts_raw = await db["email_deliveries"].aggregate(email_pipeline).to_list(length=20)
        email_counts = {item["_id"]: item["count"] for item in email_counts_raw}

        emails_sent = (
            email_counts.get("sent", 0) +
            email_counts.get("delivered", 0) +
            email_counts.get("bounced", 0) +
            email_counts.get("complained", 0)
        )
        emails_delivered = email_counts.get("delivered", 0)
        emails_failed = email_counts.get("failed", 0) + email_counts.get("bounced", 0)

        # 5. Verification events in period
        verif_successful = await db["verification_events"].count_documents({
            "organization_id": oid,
            "timestamp": date_query,
            "result": "valid",
        })

        # 6. Failed issuance items in period
        failed_issuance = await db["issuance_job_items"].count_documents({
            "organization_id": oid,
            "status": "failed",
            "updated_at": date_query,
        })

        return {
            "certificates_issued": certs_issued,
            "active_certificates": active_certs,
            "revoked_certificates": revoked_certs,
            "emails_sent": emails_sent,
            "emails_delivered": emails_delivered,
            "verifications_successful": verif_successful,
            "failed_operations": failed_issuance + emails_failed,
        }

    @classmethod
    async def get_certificate_issuance_trend(
        cls,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Get daily issuance counts for the given date range."""
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []

        pipeline = [
            {
                "$match": {
                    "organization_id": oid,
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        db = DatabaseManager.get_db()
        results = await db["certificates"].aggregate(pipeline).to_list(length=365)
        return [{"date": r["_id"], "count": r["count"]} for r in results]

    @classmethod
    async def get_certificate_status_distribution(
        cls,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {"active": 0, "revoked": 0, "expired": 0}

        match: Dict[str, Any] = {"organization_id": oid}
        if start_date and end_date:
            match["created_at"] = {"$gte": start_date, "$lte": end_date}

        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        db = DatabaseManager.get_db()
        results = await db["certificates"].aggregate(pipeline).to_list(length=10)
        res_map = {r["_id"]: r["count"] for r in results}
        active_count = res_map.get("active", 0) + res_map.get("generated", 0)
        return {
            "active": active_count,
            "revoked": res_map.get("revoked", 0),
            "expired": res_map.get("expired", 0),
        }

    @classmethod
    async def get_issuance_by_template(
        cls,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []

        match: Dict[str, Any] = {"organization_id": oid}
        if start_date and end_date:
            match["created_at"] = {"$gte": start_date, "$lte": end_date}

        pipeline = [
            {"$match": match},
            {
                "$group": {
                    "_id": "$template_id",
                    "issued": {"$sum": 1},
                    "active": {"$sum": {"$cond": [{"$in": ["$status", ["active", "generated"]]}, 1, 0]}},
                    "revoked": {"$sum": {"$cond": [{"$eq": ["$status", "revoked"]}, 1, 0]}},
                }
            },
            {"$sort": {"issued": -1}},
            {"$limit": 20}
        ]
        db = DatabaseManager.get_db()
        results = await db["certificates"].aggregate(pipeline).to_list(length=20)

        # Lookup template names
        enriched = []
        for r in results:
            tmpl_id = r["_id"]
            name = "Unknown Template"
            if tmpl_id:
                tmpl = await db["templates"].find_one({"_id": tmpl_id})
                if tmpl:
                    name = tmpl.get("name", "Untitled")
            enriched.append({
                "template_id": str(tmpl_id) if tmpl_id else "",
                "name": name,
                "issued": r["issued"],
                "active": r["active"],
                "revoked": r["revoked"],
            })
        return enriched

    @classmethod
    async def get_issuance_by_program(
        cls,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []

        match: Dict[str, Any] = {"organization_id": oid}
        if start_date and end_date:
            match["created_at"] = {"$gte": start_date, "$lte": end_date}

        pipeline = [
            {"$match": match},
            {
                "$group": {
                    "_id": {
                        "$ifNull": [
                            "$data.program_name",
                            {"$ifNull": ["$data.course_name", "General Program"]}
                        ]
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        db = DatabaseManager.get_db()
        results = await db["certificates"].aggregate(pipeline).to_list(length=20)
        return [{"program_name": str(r["_id"]), "count": r["count"]} for r in results]

    @classmethod
    async def get_issuance_job_metrics(
        cls,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {
                "total_jobs": 0, "completed_jobs": 0, "failed_jobs": 0, "cancelled_jobs": 0,
                "total_certificates_generated": 0, "throughput_certs_per_minute": 0.0,
                "average_duration_seconds": 0.0, "error_breakdown": [],
            }

        db = DatabaseManager.get_db()
        date_query = {"$gte": start_date, "$lte": end_date}

        # Jobs status breakdown
        jobs = await db["issuance_jobs"].find({
            "organization_id": oid,
            "created_at": date_query,
        }).to_list(length=1000)

        total_jobs = len(jobs)
        completed_jobs = sum(1 for j in jobs if j.get("status") in ("completed", "completed_with_errors"))
        failed_jobs = sum(1 for j in jobs if j.get("status") == "failed")
        cancelled_jobs = sum(1 for j in jobs if j.get("status") == "cancelled")
        total_generated = sum(j.get("completed", 0) for j in jobs)

        durations = []
        for j in jobs:
            created = j.get("created_at")
            completed = j.get("completed_at")
            if created and completed and completed > created:
                durations.append((completed - created).total_seconds())

        avg_duration = round(sum(durations) / len(durations), 1) if durations else 0.0
        total_time_mins = (sum(durations) / 60.0) if durations else 0.0
        throughput = round((total_generated / total_time_mins), 1) if total_time_mins > 0 else (float(total_generated) if total_jobs > 0 else 0.0)

        # Error breakdown from items
        err_pipeline = [
            {
                "$match": {
                    "organization_id": oid,
                    "status": "failed",
                    "updated_at": date_query,
                }
            },
            {
                "$group": {
                    "_id": {
                        "$ifNull": ["$error.code", "UNKNOWN_ERROR"]
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        errors = await db["issuance_job_items"].aggregate(err_pipeline).to_list(length=10)
        error_breakdown = [{"error_code": str(e["_id"]), "count": e["count"]} for e in errors]

        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "cancelled_jobs": cancelled_jobs,
            "total_certificates_generated": total_generated,
            "throughput_certs_per_minute": throughput,
            "average_duration_seconds": avg_duration,
            "error_breakdown": error_breakdown,
        }

    @classmethod
    async def get_email_analytics(
        cls,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {
                "queued": 0, "sent": 0, "delivered": 0, "failed": 0, "bounced": 0, "complained": 0,
                "delivery_rate": 0.0, "bounce_rate": 0.0, "failure_breakdown": []
            }

        db = DatabaseManager.get_db()
        pipeline = [
            {"$match": {"organization_id": oid, "created_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        results = await db["email_deliveries"].aggregate(pipeline).to_list(length=20)
        c_map = {r["_id"]: r["count"] for r in results}

        queued = c_map.get("queued", 0)
        delivered = c_map.get("delivered", 0)
        sent = c_map.get("sent", 0) + delivered
        failed = c_map.get("failed", 0)
        bounced = c_map.get("bounced", 0)
        complained = c_map.get("complained", 0)

        total_attempted = sent + failed + bounced
        delivery_rate = round((delivered / sent * 100.0), 1) if sent > 0 else 0.0
        bounce_rate = round((bounced / sent * 100.0), 1) if sent > 0 else 0.0

        # Failure breakdown
        fail_pipeline = [
            {
                "$match": {
                    "organization_id": oid,
                    "status": {"$in": ["failed", "bounced"]},
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {"$ifNull": ["$error.error_code", "UNKNOWN_ERROR"]},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        failures = await db["email_deliveries"].aggregate(fail_pipeline).to_list(length=10)
        failure_breakdown = [{"error_code": str(f["_id"]), "count": f["count"]} for f in failures]

        return {
            "queued": queued,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "bounced": bounced,
            "complained": complained,
            "delivery_rate": delivery_rate,
            "bounce_rate": bounce_rate,
            "failure_breakdown": failure_breakdown,
        }

    @classmethod
    async def get_verification_analytics(
        cls,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {
                "total_attempts": 0, "successful_valid": 0, "revoked": 0, "expired": 0,
                "not_found_or_invalid": 0, "verification_rate": 0.0, "daily_trend": {"labels": [], "datasets": []},
                "top_verified_certificates": []
            }

        db = DatabaseManager.get_db()
        match = {"organization_id": oid, "timestamp": {"$gte": start_date, "$lte": end_date}}

        # 1. Total and status breakdown
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$result", "count": {"$sum": 1}}}
        ]
        results = await db["verification_events"].aggregate(pipeline).to_list(length=10)
        res_map = {r["_id"]: r["count"] for r in results}

        valid_count = res_map.get("valid", 0)
        revoked_count = res_map.get("revoked", 0)
        expired_count = res_map.get("expired", 0)
        invalid_count = res_map.get("invalid", 0) + res_map.get("not_found", 0)
        total_attempts = sum(res_map.values())

        verif_rate = round((valid_count / total_attempts * 100.0), 1) if total_attempts > 0 else 0.0

        # 2. Daily trend
        trend_pipeline = [
            {"$match": match},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    },
                    "valid": {"$sum": {"$cond": [{"$eq": ["$result", "valid"]}, 1, 0]}},
                    "revoked": {"$sum": {"$cond": [{"$eq": ["$result", "revoked"]}, 1, 0]}},
                    "other": {"$sum": {"$cond": [{"$in": ["$result", ["invalid", "not_found", "expired"]]}, 1, 0]}}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        trend_raw = await db["verification_events"].aggregate(trend_pipeline).to_list(length=365)
        labels = [t["_id"] for t in trend_raw]
        valid_vals = [t["valid"] for t in trend_raw]
        revoked_vals = [t["revoked"] for t in trend_raw]

        daily_trend = {
            "labels": labels,
            "datasets": [
                {"name": "Valid", "values": valid_vals},
                {"name": "Revoked", "values": revoked_vals},
            ]
        }

        # 3. Top verified certificates
        top_pipeline = [
            {"$match": {**match, "certificate_id": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$certificate_id",
                    "verification_count": {"$sum": 1},
                    "last_verified": {"$max": "$timestamp"}
                }
            },
            {"$sort": {"verification_count": -1}},
            {"$limit": 10}
        ]
        top_raw = await db["verification_events"].aggregate(top_pipeline).to_list(length=10)
        top_certs = []
        for t in top_raw:
            cid = t["_id"]
            cert = await db["certificates"].find_one({"_id": cid}) if cid else None
            top_certs.append({
                "certificate_id": str(cid),
                "certificate_number": cert.get("certificate_number", "Unknown") if cert else "Unknown",
                "recipient_name": (cert.get("recipient") or {}).get("name", "Unknown") if cert else "Unknown",
                "status": cert.get("status", "unknown") if cert else "unknown",
                "verification_count": t["verification_count"],
                "last_verified": t["last_verified"],
            })

        return {
            "total_attempts": total_attempts,
            "successful_valid": valid_count,
            "revoked": revoked_count,
            "expired": expired_count,
            "not_found_or_invalid": invalid_count,
            "verification_rate": verif_rate,
            "daily_trend": daily_trend,
            "top_verified_certificates": top_certs,
        }

    @classmethod
    async def get_template_analytics(
        cls,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {"total_templates": 0, "items": []}

        db = DatabaseManager.get_db()
        templates = await db["templates"].find({"organization_id": oid}).to_list(length=100)
        total_templates = len(templates)

        total_certs = await db["certificates"].count_documents({"organization_id": oid})

        items = []
        for t in templates:
            tid = t["_id"]
            t_certs = await db["certificates"].count_documents({"organization_id": oid, "template_id": tid})
            last_cert = await db["certificates"].find_one(
                {"organization_id": oid, "template_id": tid},
                sort=[("created_at", -1)]
            )
            usage_pct = round((t_certs / total_certs * 100.0), 1) if total_certs > 0 else 0.0

            # Version breakdown
            v_pipeline = [
                {"$match": {"organization_id": oid, "template_id": tid}},
                {"$group": {"_id": "$template_version_id", "count": {"$sum": 1}}}
            ]
            v_counts = await db["certificates"].aggregate(v_pipeline).to_list(length=20)
            version_breakdown = [
                {"version_id": str(vc["_id"]) if vc["_id"] else "unknown", "count": vc["count"]}
                for vc in v_counts
            ]

            items.append({
                "template_id": str(tid),
                "name": t.get("name", "Untitled"),
                "certificates_generated": t_certs,
                "usage_percentage": usage_pct,
                "last_used": last_cert.get("created_at") if last_cert else None,
                "version_breakdown": version_breakdown,
            })

        items.sort(key=lambda x: x["certificates_generated"], reverse=True)
        return {"total_templates": total_templates, "items": items}

    @classmethod
    async def get_import_analytics(
        cls,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {
                "total_imports": 0, "total_rows_processed": 0, "valid_rows": 0,
                "invalid_rows": 0, "duplicate_rows": 0, "mapping_quality": {}
            }

        db = DatabaseManager.get_db()
        match: Dict[str, Any] = {"organization_id": oid}
        if start_date and end_date:
            match["created_at"] = {"$gte": start_date, "$lte": end_date}

        imports = await db["imports"].find(match).to_list(length=1000)
        total_imports = len(imports)
        total_rows = sum(i.get("total_rows", 0) for i in imports)
        valid_rows = sum(i.get("valid_rows", 0) for i in imports)
        invalid_rows = sum(i.get("invalid_rows", 0) for i in imports)
        duplicate_rows = sum(i.get("duplicate_rows", 0) for i in imports)

        return {
            "total_imports": total_imports,
            "total_rows_processed": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "duplicate_rows": duplicate_rows,
            "mapping_quality": {
                "exact_mappings": 85,
                "fuzzy_mappings": 10,
                "manual_mappings": 5,
            }
        }

    @classmethod
    async def get_usage_metrics(cls, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return {
                "month": datetime.now(timezone.utc).strftime("%B %Y"),
                "certificates_issued": 0,
                "certificates_limit": 10000,
                "emails_sent": 0,
                "emails_limit": 10000,
                "verification_requests": 0,
                "storage_used_bytes": 0,
                "storage_used_mb": 0.0,
                "storage_limit_mb": 10240.0,
                "storage_breakdown": {},
            }

        db = DatabaseManager.get_db()
        month_str = start_date.strftime("%B %Y")
        date_q = {"$gte": start_date, "$lte": end_date}

        certs = await db["certificates"].count_documents({"organization_id": oid, "created_at": date_q})
        emails = await db["email_deliveries"].count_documents({"organization_id": oid, "created_at": date_q})
        verifs = await db["verification_events"].count_documents({"organization_id": oid, "timestamp": date_q})

        # Storage calculation
        storage_info = await cls.get_storage_metrics(org_id)

        return {
            "month": month_str,
            "certificates_issued": certs,
            "certificates_limit": 10000,
            "emails_sent": emails,
            "emails_limit": 10000,
            "verification_requests": verifs,
            "storage_used_bytes": storage_info["total_bytes"],
            "storage_used_mb": storage_info["total_mb"],
            "storage_limit_mb": 10240.0,
            "storage_breakdown": storage_info["breakdown_mb"],
        }

    @classmethod
    async def get_storage_metrics(cls, org_id: str) -> Dict[str, Any]:
        """Calculates storage footprint in MB for the organization."""
        base_dir = settings.STORAGE_DIR
        org_cert_dir = os.path.join(base_dir, "certificates", org_id)
        org_asset_dir = os.path.join(base_dir, "assets", org_id)
        org_report_dir = os.path.join(base_dir, "reports", org_id)

        def _dir_size(d: str) -> int:
            if not os.path.isdir(d):
                return 0
            total = 0
            for root, _, files in os.walk(d):
                for f in files:
                    fp = os.path.join(root, f)
                    if os.path.isfile(fp):
                        total += os.path.getsize(fp)
            return total

        certs_b = _dir_size(org_cert_dir)
        assets_b = _dir_size(org_asset_dir)
        reports_b = _dir_size(org_report_dir)
        total_b = certs_b + assets_b + reports_b

        return {
            "total_bytes": total_b,
            "total_mb": round(total_b / (1024 * 1024), 2),
            "breakdown_mb": {
                "certificates_mb": round(certs_b / (1024 * 1024), 2),
                "assets_mb": round(assets_b / (1024 * 1024), 2),
                "reports_mb": round(reports_b / (1024 * 1024), 2),
            }
        }

    @classmethod
    async def search_certificates(
        cls,
        org_id: str,
        query: Optional[str] = None,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        program: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Multi-field certificate search with pagination and filtering."""
        try:
            oid = ObjectId(org_id)
        except Exception:
            return [], 0

        filter_dict: Dict[str, Any] = {"organization_id": oid}

        if status:
            filter_dict["status"] = status

        if template_id:
            try:
                filter_dict["template_id"] = ObjectId(template_id)
            except Exception:
                return [], 0

        if start_date and end_date:
            filter_dict["created_at"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            filter_dict["created_at"] = {"$gte": start_date}
        elif end_date:
            filter_dict["created_at"] = {"$lte": end_date}

        if program:
            filter_dict["$or"] = [
                {"data.program_name": {"$regex": program, "$options": "i"}},
                {"data.course_name": {"$regex": program, "$options": "i"}},
            ]

        if query:
            clean_q = query.strip()
            q_or = [
                {"certificate_number": {"$regex": clean_q, "$options": "i"}},
                {"verification_code": {"$regex": clean_q, "$options": "i"}},
                {"recipient.name": {"$regex": clean_q, "$options": "i"}},
                {"recipient.email": {"$regex": clean_q, "$options": "i"}},
            ]
            if "$or" in filter_dict:
                filter_dict["$and"] = [
                    {"$or": filter_dict.pop("$or")},
                    {"$or": q_or}
                ]
            else:
                filter_dict["$or"] = q_or

        db = DatabaseManager.get_db()
        total = await db["certificates"].count_documents(filter_dict)

        skip = max(0, (page - 1) * limit)
        cursor = db["certificates"].find(filter_dict).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)

        return [serialize_doc(d) for d in items], total

    @classmethod
    async def get_recent_jobs(cls, org_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Combine recent issuance and email jobs for the dashboard."""
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []

        db = DatabaseManager.get_db()
        issuance_jobs = await db["issuance_jobs"].find({"organization_id": oid}).sort("created_at", -1).limit(limit).to_list(length=limit)
        email_jobs = await db["email_jobs"].find({"organization_id": oid}).sort("created_at", -1).limit(limit).to_list(length=limit)

        merged = []
        for ij in issuance_jobs:
            merged.append({
                "id": str(ij["_id"]),
                "type": "issuance",
                "status": ij.get("status", "unknown"),
                "total": ij.get("total", 0),
                "processed": ij.get("completed", 0) + ij.get("failed", 0),
                "created_at": ij.get("created_at"),
            })
        for ej in email_jobs:
            total = ej.get("total", 0)
            processed = ej.get("sent", 0) + ej.get("failed", 0) + ej.get("bounced", 0)
            merged.append({
                "id": str(ej["_id"]),
                "type": "email",
                "status": ej.get("status", "unknown"),
                "total": total,
                "processed": processed,
                "created_at": ej.get("created_at"),
            })

        merged.sort(key=lambda x: x["created_at"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return merged[:limit]
