from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    name: str
    index: int
    sample_values: List[str] = []
    total_count: int = 0
    non_empty_count: int = 0
    empty_count: int = 0
    unique_count: int = 0
    detected_type: str = "string"


class ColumnMappingItem(BaseModel):
    source_column: Optional[str] = None
    target_field: str
    target_label: Optional[str] = None
    confidence: Optional[float] = 1.0
    confidence_level: Optional[str] = "high"  # high, medium, low, unmapped
    method: Optional[str] = "manual"  # exact, normalized, synonym, data_type, fuzzy, manual
    required: Optional[bool] = True


class ConfirmMappingRequest(BaseModel):
    mappings: List[ColumnMappingItem]
    save_as_profile: Optional[bool] = False
    profile_name: Optional[str] = None


class ValidationErrorItem(BaseModel):
    field: str
    code: str
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO


class ImportRowResponse(BaseModel):
    id: str
    import_id: str
    row_number: int
    raw_data: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    status: str = "valid"  # valid, warning, error
    errors: List[ValidationErrorItem] = []
    warnings: List[ValidationErrorItem] = []

    class Config:
        from_attributes = True


class ImportResponse(BaseModel):
    id: str
    organization_id: str
    template_id: str
    template_version_id: Optional[str] = None
    filename: str
    file_type: str
    file_size: int
    status: str  # uploaded, parsing, parsed, mapping_required, validated, ready, failed, cancelled
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    warning_rows: int = 0
    columns: List[str] = []
    column_profiles: List[ColumnProfile] = []
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportListResponse(BaseModel):
    items: List[ImportResponse]
    page: int
    limit: int
    total: int
    total_pages: int


class ImportPreviewResponse(BaseModel):
    total_rows: int
    columns: List[str]
    preview_rows: List[ImportRowResponse]
    summary: Dict[str, int]  # total, valid, warnings, errors


class MappingProfileCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    template_id: Optional[str] = None
    mappings: List[ColumnMappingItem]


class MappingProfileResponse(BaseModel):
    id: str
    organization_id: str
    template_id: Optional[str] = None
    name: str
    mappings: List[ColumnMappingItem]
    created_at: datetime

    class Config:
        from_attributes = True
