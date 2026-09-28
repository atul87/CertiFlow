import logging
from typing import Optional, List, Dict, Any, Tuple
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.schemas.template import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateListResponse,
    TemplateVersionCreateRequest,
    TemplateVersionUpdateRequest,
    TemplateVersionResponse,
    TemplateElement,
    FieldDefinition,
    PreviewResponse
)
from app.repositories.template_repository import TemplateRepository
from app.repositories.template_version_repository import TemplateVersionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.placeholder_service import PlaceholderService
from app.services.template_validator import TemplateValidator
from app.services.preview_service import PreviewService

logger = logging.getLogger(__name__)


class TemplateService:
    @classmethod
    async def create_template(
        cls,
        data: TemplateCreateRequest,
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TemplateResponse:
        # 1. Create main template document
        template_doc = await TemplateRepository.create(
            organization_id=org_id,
            name=data.name,
            description=data.description,
            created_by=user_id
        )

        # 2. Automatically create initial Version 1 Draft
        default_elements = [
            {
                "id": "cert_title",
                "type": "text",
                "content": "CERTIFICATE OF ACHIEVEMENT",
                "position": {"x": 800, "y": 600},
                "size": {"width": 1908, "height": 120},
                "style": {"font_family": "Playfair Display", "font_size": 72, "font_weight": 700, "color": "#1A1A1A", "alignment": "center"}
            },
            {
                "id": "cert_presentation",
                "type": "text",
                "content": "THIS IS PROUDLY PRESENTED TO",
                "position": {"x": 1000, "y": 800},
                "size": {"width": 1508, "height": 60},
                "style": {"font_family": "Inter", "font_size": 32, "font_weight": 400, "color": "#666666", "alignment": "center"}
            },
            {
                "id": "recipient_name",
                "type": "text",
                "content": "{{recipient_name}}",
                "position": {"x": 600, "y": 950},
                "size": {"width": 2308, "height": 140},
                "style": {"font_family": "Poppins", "font_size": 84, "font_weight": 600, "color": "#0B192C", "alignment": "center"}
            },
            {
                "id": "cert_statement",
                "type": "text",
                "content": "for successfully completing the comprehensive program in {{program_name}} on {{issue_date}}.",
                "position": {"x": 500, "y": 1200},
                "size": {"width": 2508, "height": 100},
                "style": {"font_family": "Inter", "font_size": 36, "font_weight": 400, "color": "#333333", "alignment": "center"}
            },
            {
                "id": "cert_qr",
                "type": "qr",
                "content": "{{verification_url}}",
                "position": {"x": 300, "y": 2000},
                "size": {"width": 220, "height": 220},
                "style": {}
            }
        ]

        extracted_fields = PlaceholderService.extract_fields_from_elements(default_elements)

        version_doc = await TemplateVersionRepository.create_version(
            template_id=template_doc["id"],
            organization_id=org_id,
            created_by=user_id,
            design_type="image",
            width=3508,
            height=2480,
            orientation="landscape",
            elements=default_elements,
            fields=extracted_fields,
            status="draft"
        )

        # 3. Associate v1 as current draft version
        await TemplateRepository.set_current_version(
            template_id=template_doc["id"],
            organization_id=org_id,
            version_id=version_doc["id"]
        )

        template_doc["current_version_id"] = version_doc["id"]
        template_doc["current_version"] = TemplateVersionResponse(**version_doc)

        # 4. Audit logging
        await AuditLogRepository.log_event(
            action="template.created",
            resource_type="template",
            resource_id=template_doc["id"],
            organization_id=org_id,
            user_id=user_id,
            metadata={"name": template_doc["name"]},
            ip_address=ip_address,
            user_agent=user_agent
        )

        await AuditLogRepository.log_event(
            action="template.version.created",
            resource_type="template_version",
            resource_id=version_doc["id"],
            organization_id=org_id,
            user_id=user_id,
            metadata={"version": 1, "status": "draft"},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TemplateResponse(**template_doc)

    @classmethod
    async def get_template(cls, template_id: str, org_id: str) -> TemplateResponse:
        template = await TemplateRepository.get_by_id(template_id=template_id, organization_id=org_id)
        if not template:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        # Fetch current version details
        vid = template.get("current_version_id")
        if vid:
            vdoc = await TemplateVersionRepository.get_by_id(version_id=vid, organization_id=org_id)
            if vdoc:
                template["current_version"] = TemplateVersionResponse(**vdoc)

        return TemplateResponse(**template)

    @classmethod
    async def list_templates(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = "active"
    ) -> TemplateListResponse:
        items, total = await TemplateRepository.list_templates(
            organization_id=org_id,
            page=page,
            limit=limit,
            search=search,
            status=status
        )

        # Hydrate current versions
        results = []
        for doc in items:
            vid = doc.get("current_version_id")
            if vid:
                vdoc = await TemplateVersionRepository.get_by_id(version_id=vid, organization_id=org_id)
                if vdoc:
                    doc["current_version"] = TemplateVersionResponse(**vdoc)
            results.append(TemplateResponse(**doc))

        total_pages = (total + limit - 1) // limit if total > 0 else 1
        return TemplateListResponse(
            items=results,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )

    @classmethod
    async def update_template(
        cls,
        template_id: str,
        org_id: str,
        data: TemplateUpdateRequest,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TemplateResponse:
        updates = {}
        if data.name is not None:
            updates["name"] = data.name.strip()
        if data.description is not None:
            updates["description"] = data.description.strip()
        if data.status is not None:
            updates["status"] = data.status

        if not updates:
            return await cls.get_template(template_id, org_id)

        updated = await TemplateRepository.update(
            template_id=template_id,
            organization_id=org_id,
            updates=updates
        )
        if not updated:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        await AuditLogRepository.log_event(
            action="template.updated",
            resource_type="template",
            resource_id=template_id,
            organization_id=org_id,
            user_id=user_id,
            metadata=updates,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return await cls.get_template(template_id, org_id)

    @classmethod
    async def duplicate_template(
        cls,
        template_id: str,
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TemplateResponse:
        original = await TemplateRepository.get_by_id(template_id, org_id)
        if not original:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        # 1. Create duplicate template record
        copy_name = f"{original['name']} (Copy)"
        new_template = await TemplateRepository.create(
            organization_id=org_id,
            name=copy_name,
            description=original.get("description", ""),
            created_by=user_id
        )

        # 2. Duplicate latest version as v1 draft
        latest_version = await TemplateVersionRepository.get_latest_version(template_id)
        if latest_version:
            v_elements = latest_version.get("elements", [])
            v_fields = latest_version.get("fields", [])
            new_version = await TemplateVersionRepository.create_version(
                template_id=new_template["id"],
                organization_id=org_id,
                created_by=user_id,
                design_type=latest_version.get("design_type", "image"),
                width=latest_version.get("width", 3508),
                height=latest_version.get("height", 2480),
                orientation=latest_version.get("orientation", "landscape"),
                background_asset_id=latest_version.get("background_asset_id"),
                elements=v_elements,
                fields=v_fields,
                status="draft"
            )
            await TemplateRepository.set_current_version(
                template_id=new_template["id"],
                organization_id=org_id,
                version_id=new_version["id"]
            )
            new_template["current_version_id"] = new_version["id"]
            new_template["current_version"] = TemplateVersionResponse(**new_version)

        # 3. Audit log
        await AuditLogRepository.log_event(
            action="template.duplicated",
            resource_type="template",
            resource_id=new_template["id"],
            organization_id=org_id,
            user_id=user_id,
            metadata={"original_template_id": template_id, "name": copy_name},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TemplateResponse(**new_template)

    @classmethod
    async def archive_template(
        cls,
        template_id: str,
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        archived = await TemplateRepository.archive(template_id=template_id, organization_id=org_id)
        if not archived:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        await AuditLogRepository.log_event(
            action="template.archived",
            resource_type="template",
            resource_id=template_id,
            organization_id=org_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True

    # ----------------------------------------------------
    # Version Lifecycle & Immutability
    # ----------------------------------------------------

    @classmethod
    async def create_version(
        cls,
        template_id: str,
        org_id: str,
        user_id: str,
        data: TemplateVersionCreateRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TemplateVersionResponse:
        template = await TemplateRepository.get_by_id(template_id, org_id)
        if not template:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        # Validate elements & extract fields
        elements_raw = [e.model_dump() for e in data.elements]
        TemplateValidator.validate_canvas(data.width, data.height)
        TemplateValidator.validate_elements(elements_raw, data.width, data.height)
        fields = PlaceholderService.extract_fields_from_elements(elements_raw)

        version_doc = await TemplateVersionRepository.create_version(
            template_id=template_id,
            organization_id=org_id,
            created_by=user_id,
            design_type=data.design_type,
            width=data.width,
            height=data.height,
            orientation=data.orientation,
            background_asset_id=data.background_asset_id,
            elements=elements_raw,
            fields=fields,
            status="draft"
        )

        # Set newly created version as current draft
        await TemplateRepository.set_current_version(
            template_id=template_id,
            organization_id=org_id,
            version_id=version_doc["id"]
        )

        await AuditLogRepository.log_event(
            action="template.version.created",
            resource_type="template_version",
            resource_id=version_doc["id"],
            organization_id=org_id,
            user_id=user_id,
            metadata={"template_id": template_id, "version": version_doc["version"]},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TemplateVersionResponse(**version_doc)

    @classmethod
    async def get_version(cls, version_id: str, template_id: str, org_id: str) -> TemplateVersionResponse:
        vdoc = await TemplateVersionRepository.get_by_id(version_id=version_id, organization_id=org_id)
        if not vdoc or vdoc["template_id"] != template_id:
            raise NotFoundError(message="Template version not found", code="VERSION_NOT_FOUND")
        return TemplateVersionResponse(**vdoc)

    @classmethod
    async def list_versions(cls, template_id: str, org_id: str) -> List[TemplateVersionResponse]:
        template = await TemplateRepository.get_by_id(template_id, org_id)
        if not template:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        versions = await TemplateVersionRepository.list_by_template(template_id=template_id, organization_id=org_id)
        return [TemplateVersionResponse(**v) for v in versions]

    @classmethod
    async def update_draft_version(
        cls,
        version_id: str,
        template_id: str,
        org_id: str,
        data: TemplateVersionUpdateRequest,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TemplateVersionResponse:
        vdoc = await TemplateVersionRepository.get_by_id(version_id=version_id, organization_id=org_id)
        if not vdoc or vdoc["template_id"] != template_id:
            raise NotFoundError(message="Template version not found", code="VERSION_NOT_FOUND")

        # P1.17: IMMUTABILITY ENFORCEMENT
        if vdoc.get("status") == "published":
            raise ForbiddenError(
                message="Published template versions are immutable to preserve historical certificate integrity. Create a new version draft instead.",
                code="VERSION_IMMUTABLE"
            )

        updates: Dict[str, Any] = {}
        width = data.width or vdoc.get("width", 3508)
        height = data.height or vdoc.get("height", 2480)
        TemplateValidator.validate_canvas(width, height)

        if data.width is not None:
            updates["width"] = data.width
        if data.height is not None:
            updates["height"] = data.height
        if data.orientation is not None:
            updates["orientation"] = data.orientation
        if data.background_asset_id is not None:
            updates["background_asset_id"] = data.background_asset_id

        if data.elements is not None:
            elements_raw = [e.model_dump() for e in data.elements]
            TemplateValidator.validate_elements(elements_raw, width, height)
            fields = PlaceholderService.extract_fields_from_elements(elements_raw)
            updates["elements"] = elements_raw
            updates["fields"] = fields

        updated_vdoc = await TemplateVersionRepository.update_version(
            version_id=version_id,
            organization_id=org_id,
            updates=updates
        )
        if not updated_vdoc:
            raise NotFoundError(message="Could not update template version", code="VERSION_UPDATE_FAILED")

        await AuditLogRepository.log_event(
            action="template.version.updated",
            resource_type="template_version",
            resource_id=version_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"version": updated_vdoc.get("version")},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TemplateVersionResponse(**updated_vdoc)

    @classmethod
    async def publish_version(
        cls,
        version_id: str,
        template_id: str,
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TemplateVersionResponse:
        vdoc = await TemplateVersionRepository.get_by_id(version_id=version_id, organization_id=org_id)
        if not vdoc or vdoc["template_id"] != template_id:
            raise NotFoundError(message="Template version not found", code="VERSION_NOT_FOUND")

        # P1.25: Validation before publishing
        TemplateValidator.validate_for_publish(vdoc)

        published_doc = await TemplateVersionRepository.publish_version(version_id=version_id, organization_id=org_id)
        if not published_doc:
            raise NotFoundError(message="Could not publish template version", code="PUBLISH_FAILED")

        # Set as primary published version of template
        await TemplateRepository.set_current_version(
            template_id=template_id,
            organization_id=org_id,
            version_id=version_id
        )

        await AuditLogRepository.log_event(
            action="template.version.published",
            resource_type="template_version",
            resource_id=version_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"template_id": template_id, "version": published_doc.get("version")},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TemplateVersionResponse(**published_doc)

    @classmethod
    async def generate_preview(
        cls,
        template_id: str,
        org_id: str,
        sample_data: Optional[Dict[str, Any]] = None
    ) -> PreviewResponse:
        template = await TemplateRepository.get_by_id(template_id, org_id)
        if not template:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        # Get current version or latest version
        vid = template.get("current_version_id")
        version_doc = None
        if vid:
            version_doc = await TemplateVersionRepository.get_by_id(version_id=vid, organization_id=org_id)
        if not version_doc:
            version_doc = await TemplateVersionRepository.get_latest_version(template_id)

        if not version_doc:
            raise NotFoundError(message="No design version exists for this template", code="NO_TEMPLATE_VERSION")

        preview_b64 = await PreviewService.render_preview_base64(
            version_doc=version_doc,
            sample_data=sample_data
        )

        return PreviewResponse(
            preview_url=preview_b64,
            width=version_doc.get("width", 3508),
            height=version_doc.get("height", 2480),
            format="png"
        )
