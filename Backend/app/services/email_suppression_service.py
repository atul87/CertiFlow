from __future__ import annotations
from typing import Dict, Any, List, Tuple
from app.repositories.email_suppression_repository import EmailSuppressionRepository


class EmailSuppressionService:
    @staticmethod
    async def is_suppressed(organization_id: str, email: str) -> bool:
        return await EmailSuppressionRepository.is_suppressed(organization_id, email)

    @staticmethod
    async def add_suppression(organization_id: str, email: str, reason: str = "hard_bounce") -> Dict[str, Any]:
        return await EmailSuppressionRepository.add_suppression(organization_id, email, reason)

    @staticmethod
    async def remove_suppression(organization_id: str, email: str) -> bool:
        return await EmailSuppressionRepository.remove_suppression(organization_id, email)

    @staticmethod
    async def list_suppressions(
        organization_id: str,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await EmailSuppressionRepository.list_suppressions(organization_id, page, limit)
