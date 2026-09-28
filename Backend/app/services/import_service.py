import os
import io
import csv
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from app.core.config import settings
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.schemas.imports import (
    ImportResponse,
    ImportListResponse,
    ImportPreviewResponse,
    ImportRowResponse,
    ConfirmMappingRequest,
    ColumnMappingItem,
    MappingProfileResponse,
    MappingProfileCreateRequest
)
from app.repositories.import_repository import ImportRepository
from app.repositories.import_row_repository import ImportRowRepository
from app.repositories.mapping_repository import MappingRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.template_version_repository import TemplateVersionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.csv_parser import CSVParser
from app.services.excel_parser import ExcelParser
from app.services.data_profiler import DataProfiler
from app.services.field_matcher import FieldMatcher
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)

MAX_IMPORT_SIZE_BYTES = 25 * 1024 * 1024  # 25MB


class ImportService:
    @classmethod
    def _get_storage_path(cls, org_id: str, import_id: str, filename: str) -> Tuple[str, Path]:
        base_dir = Path(settings.STORAGE_DIR) / "imports" / org_id / import_id
        base_dir.mkdir(parents=True, exist_ok=True)
        target_path = base_dir / filename
        storage_key = str((Path("imports") / org_id / import_id / filename).as_posix())
        return storage_key, target_path

    @classmethod
    async def create_and_parse_import(
        cls,
        content: bytes,
        filename: str,
        template_id: str,
        template_version_id: Optional[str],
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ImportResponse:
        # 1. Validate file size and extension
        if len(content) > MAX_IMPORT_SIZE_BYTES:
            raise ValidationError(message="File exceeds maximum allowed size of 25MB", code="FILE_TOO_LARGE")

        if len(content) == 0:
            raise ValidationError(message="Uploaded file is empty", code="EMPTY_FILE")

        ext = Path(filename).suffix.lower()
        if ext not in [".csv", ".xlsx", ".xls"]:
            raise ValidationError(
                message=f"Unsupported file format '{ext}'. Allowed: .csv, .xlsx, .xls",
                code="UNSUPPORTED_FILE_TYPE"
            )

        file_type = "csv" if ext == ".csv" else "xlsx"

        # 2. Verify template and version belong to this organization
        template = await TemplateRepository.get_by_id(template_id, org_id)
        if not template:
            raise NotFoundError(message="Template not found", code="TEMPLATE_NOT_FOUND")

        v_id = template_version_id or template.get("current_version_id")
        if not v_id:
            latest_v = await TemplateVersionRepository.get_latest_version(template_id)
            if not latest_v:
                raise NotFoundError(message="Template has no design versions", code="NO_TEMPLATE_VERSION")
            v_id = latest_v["id"]

        version_doc = await TemplateVersionRepository.get_by_id(v_id, org_id)
        if not version_doc:
            raise NotFoundError(message="Template version not found", code="VERSION_NOT_FOUND")

        # 3. Create initial Import record
        import_record = await ImportRepository.create(
            organization_id=org_id,
            template_id=template_id,
            template_version_id=v_id,
            filename=filename,
            file_type=file_type,
            file_size=len(content),
            storage_key="",
            created_by=user_id
        )

        import_id = import_record["id"]

        # 4. Save original file to storage
        storage_key, file_path = cls._get_storage_path(org_id, import_id, filename)
        with open(file_path, "wb") as f:
            f.write(content)

        await ImportRepository.update(import_id, org_id, {"storage_key": storage_key, "status": "parsing"})

        # 5. Parse file
        try:
            if file_type == "csv":
                columns, rows = CSVParser.parse(content)
            else:
                columns, rows = ExcelParser.parse(content, filename)
        except Exception as e:
            await ImportRepository.update(import_id, org_id, {
                "status": "failed",
                "error_message": str(e)
            })
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(message=f"Failed to parse spreadsheet: {str(e)}", code="PARSE_FAILED")

        # 6. Profile columns
        profiles = DataProfiler.profile_columns(columns, rows)

        # 7. Check for saved mapping profiles or auto-suggest mappings
        template_fields = cls._get_effective_template_fields(version_doc)
        suggested_mappings = FieldMatcher.suggest_mappings(columns, profiles, template_fields)

        # Save initial suggested mappings in import_mappings
        await MappingRepository.save_mapping(
            import_id=import_id,
            template_version_id=v_id,
            organization_id=org_id,
            mappings=suggested_mappings,
            confirmed_by=user_id
        )

        # 8. Update import status to 'mapping_required'
        updated = await ImportRepository.update(import_id, org_id, {
            "status": "mapping_required",
            "columns": columns,
            "column_profiles": profiles,
            "total_rows": len(rows)
        })

        # 9. Audit logs
        await AuditLogRepository.log_event(
            action="import.created",
            resource_type="import",
            resource_id=import_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={"filename": filename, "total_rows": len(rows)},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return ImportResponse(**updated)

    @classmethod
    async def get_import(cls, import_id: str, org_id: str) -> ImportResponse:
        rec = await ImportRepository.get_by_id(import_id, org_id)
        if not rec:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")
        return ImportResponse(**rec)

    @classmethod
    async def list_imports(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> ImportListResponse:
        items, total = await ImportRepository.list_imports(
            organization_id=org_id,
            page=page,
            limit=limit,
            status=status,
            template_id=template_id
        )
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        return ImportListResponse(
            items=[ImportResponse(**i) for i in items],
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )

    @staticmethod
    def _get_effective_template_fields(version_doc: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fields = [dict(f) for f in version_doc.get("fields", [])] if version_doc else []
        existing_keys = {f.get("key") for f in fields}
        if "recipient_email" not in existing_keys:
            fields.append({
                "key": "recipient_email",
                "label": "Recipient Email",
                "type": "email",
                "required": False,
                "source": "recipient",
                "description": "Recipient email address for certificate delivery"
            })
        return fields

    @classmethod
    async def get_mapping(cls, import_id: str, org_id: str) -> Dict[str, Any]:
        rec = await ImportRepository.get_by_id(import_id, org_id)
        if not rec:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")

        mapping_doc = await MappingRepository.get_mapping(import_id, org_id)
        if mapping_doc:
            return mapping_doc

        # Generate on the fly if not yet persisted
        version_doc = await TemplateVersionRepository.get_by_id(rec["template_version_id"], org_id)
        template_fields = cls._get_effective_template_fields(version_doc)
        suggestions = FieldMatcher.suggest_mappings(rec["columns"], rec["column_profiles"], template_fields)
        return {"mappings": suggestions}

    @classmethod
    async def confirm_mapping_and_validate(
        cls,
        import_id: str,
        org_id: str,
        data: ConfirmMappingRequest,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ImportResponse:
        imp = await ImportRepository.get_by_id(import_id, org_id)
        if not imp:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")

        version_doc = await TemplateVersionRepository.get_by_id(imp["template_version_id"], org_id)
        if not version_doc:
            raise NotFoundError(message="Template version not found", code="VERSION_NOT_FOUND")

        template_fields = cls._get_effective_template_fields(version_doc)

        # 1. Validation of mapping payload:
        # Check no duplicate mapping to same target field
        seen_targets = set()
        raw_mappings = [m.model_dump() for m in data.mappings]
        for m in raw_mappings:
            target = m.get("target_field")
            src = m.get("source_column")
            if target and src:
                if target in seen_targets:
                    raise ValidationError(
                        message=f"Multiple columns cannot be mapped to the same target field: '{target}'",
                        code="DUPLICATE_TARGET_MAPPING"
                    )
                seen_targets.add(target)

        # Check required fields mapped
        for f in template_fields:
            if f.get("source") != "system" and f.get("required", True):
                if f["key"] not in seen_targets:
                    raise ValidationError(
                        message=f"Required template field '{f.get('label', f['key'])}' is not mapped",
                        code="MISSING_REQUIRED_FIELD_MAPPING"
                    )

        # 2. Save confirmed mapping
        await MappingRepository.save_mapping(
            import_id=import_id,
            template_version_id=imp["template_version_id"],
            organization_id=org_id,
            mappings=raw_mappings,
            confirmed_by=user_id
        )

        # 3. Optional: Save mapping profile
        if data.save_as_profile and data.profile_name:
            await MappingRepository.create_profile(
                organization_id=org_id,
                name=data.profile_name,
                template_id=imp.get("template_id"),
                mappings=raw_mappings
            )

        # 4. Re-read original file and perform row-level validation
        storage_key = imp.get("storage_key")
        full_path = Path(settings.STORAGE_DIR) / storage_key
        if not full_path.is_file():
            raise NotFoundError(message="Original upload file is missing from storage", code="FILE_NOT_FOUND")

        with open(full_path, "rb") as f:
            content = f.read()

        if imp["file_type"] == "csv":
            _, raw_rows = CSVParser.parse(content)
        else:
            _, raw_rows = ExcelParser.parse(content, imp["filename"])

        validated_rows = []
        invalid_count = 0
        warning_count = 0
        valid_count = 0

        for idx, row in enumerate(raw_rows):
            row_num = idx + 1
            v_res = ValidationService.validate_row(
                row_number=row_num,
                raw_row=row,
                mappings=raw_mappings,
                template_fields=template_fields
            )
            if v_res["status"] == "error":
                invalid_count += 1
            elif v_res["status"] == "warning":
                warning_count += 1
            else:
                valid_count += 1

            validated_rows.append(v_res)

        # Flag dataset duplicates (updates warnings and warning_count)
        ValidationService.flag_dataset_duplicates(validated_rows)

        # Recount after duplicate pass
        warning_count = sum(1 for r in validated_rows if r["status"] == "warning")
        valid_count = sum(1 for r in validated_rows if r["status"] == "valid")
        invalid_count = sum(1 for r in validated_rows if r["status"] == "error")

        # 5. Bulk insert rows into import_rows
        await ImportRowRepository.bulk_insert(
            import_id=import_id,
            organization_id=org_id,
            validated_rows=validated_rows
        )

        # 6. Set final import status
        # If no invalid rows exist, status transitions to READY!
        final_status = "ready" if invalid_count == 0 else "validated"

        updated = await ImportRepository.update(import_id, org_id, {
            "status": final_status,
            "total_rows": len(raw_rows),
            "valid_rows": valid_count,
            "invalid_rows": invalid_count,
            "warning_rows": warning_count
        })

        # 7. Audit log
        await AuditLogRepository.log_event(
            action="import.validation.completed",
            resource_type="import",
            resource_id=import_id,
            organization_id=org_id,
            user_id=user_id,
            metadata={
                "status": final_status,
                "total": len(raw_rows),
                "valid": valid_count,
                "invalid": invalid_count,
                "warnings": warning_count
            },
            ip_address=ip_address,
            user_agent=user_agent
        )

        return ImportResponse(**updated)

    @classmethod
    async def get_preview(cls, import_id: str, org_id: str) -> ImportPreviewResponse:
        imp = await ImportRepository.get_by_id(import_id, org_id)
        if not imp:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")

        preview_rows = await ImportRowRepository.get_preview_rows(import_id, org_id, limit=20)
        return ImportPreviewResponse(
            total_rows=imp.get("total_rows", 0),
            columns=imp.get("columns", []),
            preview_rows=[ImportRowResponse(**r) for r in preview_rows],
            summary={
                "total": imp.get("total_rows", 0),
                "valid": imp.get("valid_rows", 0),
                "warnings": imp.get("warning_rows", 0),
                "errors": imp.get("invalid_rows", 0)
            }
        )

    @classmethod
    async def list_rows(
        cls,
        import_id: str,
        org_id: str,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        imp = await ImportRepository.get_by_id(import_id, org_id)
        if not imp:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")

        rows, total = await ImportRowRepository.list_rows(
            import_id=import_id,
            organization_id=org_id,
            page=page,
            limit=limit,
            status=status
        )
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        return {
            "items": [ImportRowResponse(**r) for r in rows],
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }

    @classmethod
    async def get_error_rows(cls, import_id: str, org_id: str) -> List[ImportRowResponse]:
        imp = await ImportRepository.get_by_id(import_id, org_id)
        if not imp:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")

        error_rows = await ImportRowRepository.get_error_rows(import_id, org_id)
        return [ImportRowResponse(**r) for r in error_rows]

    @classmethod
    async def generate_error_csv(cls, import_id: str, org_id: str) -> str:
        imp = await ImportRepository.get_by_id(import_id, org_id)
        if not imp:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")

        error_rows = await ImportRowRepository.get_error_rows(import_id, org_id)
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["Row Number", "Recipient Name", "Recipient Email", "Error Code", "Error Message", "Field"])

        for r in error_rows:
            raw = r.get("raw_data", {})
            name = raw.get("Name") or raw.get("name") or raw.get("Student Name") or raw.get("recipient_name") or ""
            email = raw.get("Email") or raw.get("email") or raw.get("Email Address") or raw.get("recipient_email") or ""
            for err in r.get("errors", []):
                writer.writerow([
                    r.get("row_number"),
                    name,
                    email,
                    err.get("code"),
                    err.get("message"),
                    err.get("field")
                ])

        return out.getvalue()

    @classmethod
    async def cancel_import(
        cls,
        import_id: str,
        org_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        cancelled = await ImportRepository.update(import_id, org_id, {"status": "cancelled"})
        if not cancelled:
            raise NotFoundError(message="Import not found", code="IMPORT_NOT_FOUND")

        await AuditLogRepository.log_event(
            action="import.cancelled",
            resource_type="import",
            resource_id=import_id,
            organization_id=org_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True

    # Mapping Profiles
    @classmethod
    async def create_mapping_profile(
        cls,
        data: MappingProfileCreateRequest,
        org_id: str
    ) -> MappingProfileResponse:
        raw_mappings = [m.model_dump() for m in data.mappings]
        doc = await MappingRepository.create_profile(
            organization_id=org_id,
            name=data.name,
            template_id=data.template_id,
            mappings=raw_mappings
        )
        return MappingProfileResponse(**doc)

    @classmethod
    async def list_mapping_profiles(
        cls,
        org_id: str,
        template_id: Optional[str] = None
    ) -> List[MappingProfileResponse]:
        docs = await MappingRepository.list_profiles(organization_id=org_id, template_id=template_id)
        return [MappingProfileResponse(**d) for d in docs]

    @classmethod
    async def delete_mapping_profile(
        cls,
        profile_id: str,
        org_id: str
    ) -> bool:
        deleted = await MappingRepository.delete_profile(profile_id, org_id)
        if not deleted:
            raise NotFoundError(message="Mapping profile not found", code="PROFILE_NOT_FOUND")
        return True
