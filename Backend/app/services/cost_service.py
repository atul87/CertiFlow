from __future__ import annotations
from typing import Dict, Any, Optional
from app.core.config import settings
from app.repositories.usage_counter_repository import UsageCounterRepository
from app.services.usage_service import UsageService


class CostService:
    @classmethod
    async def get_org_cost_breakdown(
        cls,
        org_id: str,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate infrastructure computing and delivery costs incurred by an organization
        in the specified billing period (in INR or local currency).
        """
        p = period or UsageService.current_period()
        counters = await UsageCounterRepository.get_all_for_period(org_id, p)

        certs = counters.get("certificates_generated", 0)
        emails = counters.get("emails_sent", 0)
        storage_bytes = counters.get("storage_bytes", 0)

        storage_gb = storage_bytes / (1024 ** 3)
        cert_cost = certs * getattr(settings, "COST_PER_CERTIFICATE", 0.05)
        email_cost = emails * getattr(settings, "COST_PER_EMAIL", 0.01)
        storage_cost = storage_gb * getattr(settings, "COST_PER_GB_STORAGE_MONTHLY", 2.0)
        total_estimated_cost = round(cert_cost + email_cost + storage_cost, 2)

        breakdown = {
            "certificates": {
                "count": certs,
                "unit_cost": getattr(settings, "COST_PER_CERTIFICATE", 0.05),
                "total_cost": round(cert_cost, 2)
            },
            "emails": {
                "count": emails,
                "unit_cost": getattr(settings, "COST_PER_EMAIL", 0.01),
                "total_cost": round(email_cost, 2)
            },
            "storage": {
                "gigabytes": round(storage_gb, 3),
                "unit_cost_per_gb": getattr(settings, "COST_PER_GB_STORAGE_MONTHLY", 2.0),
                "total_cost": round(storage_cost, 2)
            }
        }

        return {
            "period": p,
            "currency": getattr(settings, "BILLING_CURRENCY", "INR"),
            "total_estimated_cost": total_estimated_cost,
            "total_estimated_cost_inr": total_estimated_cost,
            "certificates_generated": certs,
            "cost_per_certificate_inr": getattr(settings, "COST_PER_CERTIFICATE", 0.05),
            "breakdown": breakdown,
            "cost_breakdown": breakdown
        }

    estimate_monthly_cost = get_org_cost_breakdown
