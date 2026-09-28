from __future__ import annotations
from typing import Dict, Any, List
from app.repositories.plan_repository import PlanRepository, DEFAULT_PLANS
from app.schemas.plan import PlanResponse, PlanListResponse
from app.core.exceptions import NotFoundError


class PlanService:
    @classmethod
    async def list_plans(cls) -> PlanListResponse:
        """List all active subscription plans with full entitlement matrices."""
        plans = await PlanRepository.list_active_plans()
        return PlanListResponse(
            items=[PlanResponse(**p) for p in plans],
            total=len(plans)
        )

    @classmethod
    async def get_plan(cls, plan_id: str) -> PlanResponse:
        """Fetch plan details by plan_id."""
        plan = await PlanRepository.get_by_id(plan_id)
        if not plan:
            raise NotFoundError(message=f"Plan '{plan_id}' not found", code="PLAN_NOT_FOUND")
        return PlanResponse(**plan)

    @classmethod
    async def list_active_plans(cls) -> List[Dict[str, Any]]:
        """Direct access to active plan records."""
        return await PlanRepository.list_active_plans()

