from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List, Tuple
from app.repositories.achievement_repository import AchievementRepository
from app.schemas.achievement import AchievementCreateRequest, AchievementUpdateRequest
from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class AchievementService:
    @classmethod
    async def create_achievement(cls, organization_id: str, data: AchievementCreateRequest) -> Dict[str, Any]:
        return await AchievementRepository.create(
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            criteria=data.criteria,
            skills=data.skills,
            category=data.category or "certification",
            level=data.level,
            image=data.image,
            url=data.url,
            credits=data.credits
        )

    @classmethod
    async def get_achievement(cls, achievement_id: str, organization_id: Optional[str] = None) -> Dict[str, Any]:
        item = await AchievementRepository.get_by_id(achievement_id, organization_id)
        if not item:
            raise NotFoundError(message=f"Achievement '{achievement_id}' not found", code="ACHIEVEMENT_NOT_FOUND")
        return item

    @classmethod
    async def list_achievements(
        cls,
        organization_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await AchievementRepository.list_by_org(organization_id, skip=skip, limit=limit)

    @classmethod
    async def update_achievement(
        cls,
        achievement_id: str,
        organization_id: str,
        data: AchievementUpdateRequest
    ) -> Dict[str, Any]:
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        updated = await AchievementRepository.update(achievement_id, organization_id, updates)
        if not updated:
            raise NotFoundError(message=f"Achievement '{achievement_id}' not found", code="ACHIEVEMENT_NOT_FOUND")
        return updated

    @classmethod
    async def delete_achievement(cls, achievement_id: str, organization_id: str) -> bool:
        deleted = await AchievementRepository.delete(achievement_id, organization_id)
        if not deleted:
            raise NotFoundError(message=f"Achievement '{achievement_id}' not found", code="ACHIEVEMENT_NOT_FOUND")
        return True

    @classmethod
    async def get_or_create_from_template(cls, organization_id: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derives or links an achievement from certificate template metadata.
        Enables seamless zero-friction issuance of digital credentials for any certificate.
        """
        template_name = template.get("name") or "Standard Certificate of Completion"
        description = template.get("description") or f"Successfully completed all requirements for {template_name}."
        criteria = f"Satisfactory completion of evaluation criteria specified by {template_name}."

        # Check if an achievement with this name already exists for the org
        items, _ = await AchievementRepository.list_by_org(organization_id, limit=100)
        for item in items:
            if item["name"].strip().lower() == template_name.strip().lower():
                return item

        # Create new achievement record
        return await AchievementRepository.create(
            organization_id=organization_id,
            name=template_name,
            description=description,
            criteria=criteria,
            skills=template.get("tags") or ["Professional Certification"],
            category="certification"
        )
