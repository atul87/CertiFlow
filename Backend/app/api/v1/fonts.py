from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.schemas.asset import FontResponse
from app.repositories.font_repository import FontRepository

router = APIRouter(prefix="/fonts", tags=["Fonts"])


@router.get(
    "",
    response_model=APIResponse[List[FontResponse]],
    summary="List all available system and custom fonts for certificate design"
)
async def list_fonts(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    fonts = await FontRepository.list_available_fonts(organization_id=context.get("org_id"))
    return APIResponse.ok([FontResponse(**f) for f in fonts])
