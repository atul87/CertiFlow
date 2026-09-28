from __future__ import annotations
from fastapi import APIRouter, status
from app.schemas.common import APIResponse
from app.schemas.plan import PlanListResponse, PlanResponse
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["SaaS Plans & Pricing"])


@router.get(
    "",
    response_model=APIResponse[PlanListResponse],
    status_code=status.HTTP_200_OK,
    summary="List all available SaaS subscription tiers and entitlements"
)
async def list_plans():
    plans = await PlanService.list_plans()
    return APIResponse.ok(plans)


@router.get(
    "/{plan_id}",
    response_model=APIResponse[PlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Get details and limits for a specific plan tier"
)
async def get_plan(plan_id: str):
    plan = await PlanService.get_plan(plan_id)
    return APIResponse.ok(plan)
