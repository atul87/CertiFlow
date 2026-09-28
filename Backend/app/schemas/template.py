from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class ElementPosition(BaseModel):
    x: float = Field(0, description="X coordinate in pixels")
    y: float = Field(0, description="Y coordinate in pixels")


class ElementSize(BaseModel):
    width: float = Field(100, gt=0, description="Width in pixels")
    height: float = Field(50, gt=0, description="Height in pixels")


class ElementStyle(BaseModel):
    font_family: str = Field("Poppins", description="CSS font family name")
    font_size: int = Field(48, gt=0, description="Font size in points/pixels")
    font_weight: Union[int, str] = Field(400, description="Font weight (e.g. 400, 600, 700 or 'bold')")
    color: str = Field("#000000", description="Hex or CSS color")
    alignment: str = Field("center", description="Text alignment: left, center, right, justify")
    opacity: float = Field(1.0, ge=0.0, le=1.0)
    line_height: Optional[float] = Field(1.2, description="Line height multiplier")
    letter_spacing: Optional[float] = Field(0.0, description="Letter spacing in px")


class TemplateElement(BaseModel):
    id: str = Field(..., description="Unique element identifier")
    type: str = Field("text", description="Element type: text, image, shape, line, qr")
    content: Optional[str] = Field("", description="Element text, URL, or placeholder (e.g. {{recipient_name}})")
    position: ElementPosition = Field(default_factory=ElementPosition)
    size: ElementSize = Field(default_factory=ElementSize)
    style: Optional[ElementStyle] = Field(default_factory=ElementStyle)
    asset_id: Optional[str] = Field(None, description="Referenced asset id for images/logos/signatures")


class FieldDefinition(BaseModel):
    key: str = Field(..., description="Placeholder key, e.g. recipient_name")
    label: str = Field(..., description="Human-readable label, e.g. Recipient Name")
    type: str = Field("text", description="Field data type: text, date, number, url, image")
    required: bool = Field(True, description="Whether field is required for generation")
    source: str = Field("recipient", description="'recipient' for user CSV data, 'system' for automated fields")
    description: Optional[str] = None


class TemplateCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Template name")
    description: Optional[str] = Field("", max_length=500, description="Template description")

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Template name cannot be empty")
        return cleaned


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, description="'active' or 'archived'")


class TemplateVersionCreateRequest(BaseModel):
    design_type: str = Field("image", description="Design type: image, pdf, svg, html")
    width: int = Field(3508, ge=500, le=10000, description="Canvas width (default: A4 landscape 300DPI)")
    height: int = Field(2480, ge=300, le=10000, description="Canvas height (default: A4 landscape 300DPI)")
    orientation: str = Field("landscape", description="landscape or portrait")
    background_asset_id: Optional[str] = Field(None, description="Asset ID of certificate background image")
    elements: List[TemplateElement] = Field(default_factory=list)


class TemplateVersionUpdateRequest(BaseModel):
    width: Optional[int] = Field(None, ge=500, le=10000)
    height: Optional[int] = Field(None, ge=300, le=10000)
    orientation: Optional[str] = None
    background_asset_id: Optional[str] = None
    elements: Optional[List[TemplateElement]] = None


class TemplateVersionResponse(BaseModel):
    id: str
    template_id: str
    organization_id: str
    version: int
    status: str  # draft, published, archived
    design_type: str
    width: int
    height: int
    orientation: str
    background_asset_id: Optional[str] = None
    elements: List[TemplateElement] = []
    fields: List[FieldDefinition] = []
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = ""
    status: str  # active, archived
    current_version_id: Optional[str] = None
    current_version: Optional[TemplateVersionResponse] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    items: List[TemplateResponse]
    page: int
    limit: int
    total: int
    total_pages: int


class PreviewRequest(BaseModel):
    sample_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom values for placeholders")


class PreviewResponse(BaseModel):
    preview_url: str
    width: int
    height: int
    format: str = "png"
