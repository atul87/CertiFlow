import logging
from typing import List, Optional, Dict, Any
from app.core.exceptions import NotFoundError, ForbiddenError
from app.schemas.asset import AssetResponse
from app.repositories.asset_repository import AssetRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class AssetService:
    @classmethod
    async def upload_asset(
        cls,
        content: bytes,
        filename: str,
        asset_type: str,
        org_id: str,
        user_id: str,
        template_id: Optional[str] = None,
        content_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AssetResponse:
        # 1. Validate file
        meta = StorageService.validate_file(filename=filename, content=content, content_type=content_type)

        # 2. Save file
        storage_key, _ = StorageService.save_file(
            content=content,
            filename=filename,
            org_id=org_id,
            template_id=template_id
        )

        # 3. Create database record
        doc = await AssetRepository.create(
            organization_id=org_id,
            filename=filename,
            mime_type=meta["mime_type"],
            size=meta["size"],
            storage_key=storage_key,
            asset_type=asset_type,
            width=meta["width"],
            height=meta["height"],
            created_by=user_id,
            template_id=template_id
        )

        # 4. Audit log
        await AuditLogRepository.log_event(
            action="template.asset.uploaded",
            resource_type="asset",
            resource_id=doc["id"],
            organization_id=org_id,
            user_id=user_id,
            metadata={"filename": filename, "asset_type": asset_type, "size": meta["size"]},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return AssetResponse(**doc)

    @classmethod
    async def list_template_assets(cls, template_id: str, org_id: str) -> List[AssetResponse]:
        docs = await AssetRepository.list_by_template(template_id=template_id, organization_id=org_id)
        return [AssetResponse(**d) for d in docs]

    @classmethod
    async def delete_asset(
        cls,
        asset_id: str,
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        deleted = await AssetRepository.delete(asset_id=asset_id, organization_id=org_id)
        if not deleted:
            raise NotFoundError(message="Asset not found or already deleted", code="ASSET_NOT_FOUND")

        await AuditLogRepository.log_event(
            action="template.asset.deleted",
            resource_type="asset",
            resource_id=asset_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"filename": deleted.get("filename")},
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True
