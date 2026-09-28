from __future__ import annotations
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.schemas.achievement import (
    AchievementCreateRequest,
    AchievementUpdateRequest,
    AchievementResponse,
    AchievementListResponse,
)
from app.services.achievement_service import AchievementService

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.post("", response_model=APIResponse[AchievementResponse], status_code=status.HTTP_201_CREATED)
async def create_achievement(
    body: AchievementCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    item = await AchievementService.create_achievement(org_id, body)
    return APIResponse.created(AchievementResponse(**item))


@router.get("", response_model=APIResponse[AchievementListResponse])
async def list_achievements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    items, total = await AchievementService.list_achievements(org_id, skip=skip, limit=limit)
    return APIResponse.ok(AchievementListResponse(
        items=[AchievementResponse(**it) for it in items],
        total=total
    ))


@router.get("/{achievement_id}", response_model=APIResponse[AchievementResponse])
async def get_achievement(
    achievement_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    item = await AchievementService.get_achievement(achievement_id, org_id)
    return APIResponse.ok(AchievementResponse(**item))


@router.put("/{achievement_id}", response_model=APIResponse[AchievementResponse])
async def update_achievement(
    achievement_id: str,
    body: AchievementUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    updated = await AchievementService.update_achievement(achievement_id, org_id, body)
    return APIResponse.ok(AchievementResponse(**updated))


@router.delete("/{achievement_id}", response_model=APIResponse[Dict[str, bool]])
async def delete_achievement(
    achievement_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org_id = context["organization"]["id"]
    await AchievementService.delete_achievement(achievement_id, org_id)
    return APIResponse.ok({"deleted": True})
