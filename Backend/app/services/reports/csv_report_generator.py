from __future__ import annotations
import csv
import io
from typing import AsyncGenerator, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager


class CSVReportGenerator:

    @classmethod
    async def generate_certificate_csv(
        cls,
        org_id: str,
        filters: Dict[str, Any],
        batch_size: int = 500,
    ) -> Tuple[bytes, int]:
        db = DatabaseManager.get_db()
        match: Dict[str, Any] = {"organization_id": ObjectId(org_id)}

        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        if start_date and end_date:
            match["created_at"] = {"$gte": start_date, "$lte": end_date}
        if filters.get("status"):
            match["status"] = filters["status"]
        if filters.get("template_id"):
            try:
                match["template_id"] = ObjectId(filters["template_id"])
            except Exception:
                pass

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "certificate_number",
            "recipient_name",
            "recipient_email",
            "program_name",
            "status",
            "issued_at",
            "verification_code",
            "email_status",
        ])

        count = 0
        cursor = db["certificates"].find(match).sort("created_at", -1)
        async for cert in cursor:
            count += 1
            rec = cert.get("recipient", {})
            data = cert.get("data", {})
            email_deliv = cert.get("email_delivery", {})
            writer.writerow([
                cert.get("certificate_number", ""),
                rec.get("name", ""),
                rec.get("email", ""),
                data.get("program_name") or data.get("course_name") or "",
                cert.get("status", "active"),
                cert.get("created_at", ""),
                cert.get("verification_code", ""),
                email_deliv.get("status", "none"),
            ])

        return output.getvalue().encode("utf-8"), count

    @classmethod
    async def generate_email_csv(
        cls,
        org_id: str,
        filters: Dict[str, Any],
    ) -> Tuple[bytes, int]:
        db = DatabaseManager.get_db()
        match: Dict[str, Any] = {"organization_id": ObjectId(org_id)}

        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        if start_date and end_date:
            match["created_at"] = {"$gte": start_date, "$lte": end_date}
        if filters.get("status"):
            match["status"] = filters["status"]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "delivery_id",
            "certificate_id",
            "recipient_email",
            "recipient_name",
            "status",
            "provider",
            "attempts",
            "sent_at",
            "delivered_at",
            "failed_at",
            "error_code",
            "error_message",
        ])

        count = 0
        cursor = db["email_deliveries"].find(match).sort("created_at", -1)
        async for deliv in cursor:
            count += 1
            err = deliv.get("error") or {}
            writer.writerow([
                str(deliv.get("_id", "")),
                str(deliv.get("certificate_id", "")),
                deliv.get("recipient_email", ""),
                deliv.get("recipient_name", ""),
                deliv.get("status", ""),
                deliv.get("provider", ""),
                deliv.get("attempts", 0),
                deliv.get("sent_at", ""),
                deliv.get("delivered_at", ""),
                deliv.get("failed_at", ""),
                err.get("error_code", ""),
                err.get("message", ""),
            ])

        return output.getvalue().encode("utf-8"), count

    @classmethod
    async def generate_verification_csv(
        cls,
        org_id: str,
        filters: Dict[str, Any],
    ) -> Tuple[bytes, int]:
        db = DatabaseManager.get_db()
        match: Dict[str, Any] = {"organization_id": ObjectId(org_id)}

        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        if start_date and end_date:
            match["timestamp"] = {"$gte": start_date, "$lte": end_date}
        if filters.get("result"):
            match["result"] = filters["result"]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "event_id",
            "verification_code",
            "certificate_id",
            "result",
            "timestamp",
            "user_agent",
        ])

        count = 0
        cursor = db["verification_events"].find(match).sort("timestamp", -1)
        async for ev in cursor:
            count += 1
            writer.writerow([
                str(ev.get("_id", "")),
                ev.get("verification_code", ""),
                str(ev.get("certificate_id", "")),
                ev.get("result", ""),
                ev.get("timestamp", ""),
                ev.get("user_agent", ""),
            ])

        return output.getvalue().encode("utf-8"), count

    @classmethod
    async def generate_activity_csv(
        cls,
        org_id: str,
        filters: Dict[str, Any],
    ) -> Tuple[bytes, int]:
        db = DatabaseManager.get_db()
        match: Dict[str, Any] = {"organization_id": ObjectId(org_id)}

        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        if start_date and end_date:
            match["created_at"] = {"$gte": start_date, "$lte": end_date}
        if filters.get("action"):
            match["action"] = filters["action"]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "timestamp",
            "user_id",
            "action",
            "resource_type",
            "resource_id",
            "ip_address",
        ])

        count = 0
        cursor = db["audit_logs"].find(match).sort("created_at", -1)
        async for log in cursor:
            count += 1
            writer.writerow([
                log.get("created_at", ""),
                str(log.get("user_id", "")),
                log.get("action", ""),
                log.get("resource_type", ""),
                str(log.get("resource_id", "")),
                log.get("ip_address", ""),
            ])

        return output.getvalue().encode("utf-8"), count
