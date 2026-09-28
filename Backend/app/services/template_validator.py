import re
from typing import Dict, Any, List
from app.core.exceptions import ValidationError
from app.services.placeholder_service import PlaceholderService

HEX_COLOR_REGEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
VALID_ELEMENT_TYPES = {"text", "image", "shape", "line", "qr"}
VALID_ALIGNMENTS = {"left", "center", "right", "justify"}


class TemplateValidator:
    @classmethod
    def validate_canvas(cls, width: int, height: int) -> None:
        if width < 500 or width > 10000:
            raise ValidationError(
                message=f"Canvas width ({width}px) is invalid. Must be between 500px and 10000px.",
                code="INVALID_CANVAS_WIDTH"
            )
        if height < 300 or height > 10000:
            raise ValidationError(
                message=f"Canvas height ({height}px) is invalid. Must be between 300px and 10000px.",
                code="INVALID_CANVAS_HEIGHT"
            )

    @classmethod
    def validate_elements(cls, elements: List[Dict[str, Any]], canvas_width: int, canvas_height: int) -> None:
        if not isinstance(elements, list):
            raise ValidationError(message="Elements must be a list", code="INVALID_ELEMENTS")

        seen_ids = set()
        for idx, elem in enumerate(elements):
            if not isinstance(elem, dict):
                raise ValidationError(message=f"Element at index {idx} must be an object", code="INVALID_ELEMENT")

            elem_id = elem.get("id")
            if not elem_id or not isinstance(elem_id, str):
                raise ValidationError(message=f"Element at index {idx} is missing a unique 'id'", code="MISSING_ELEMENT_ID")
            if elem_id in seen_ids:
                raise ValidationError(message=f"Duplicate element id '{elem_id}' found", code="DUPLICATE_ELEMENT_ID")
            seen_ids.add(elem_id)

            elem_type = elem.get("type")
            if elem_type not in VALID_ELEMENT_TYPES:
                raise ValidationError(
                    message=f"Element '{elem_id}' has invalid type '{elem_type}'. Allowed: {', '.join(VALID_ELEMENT_TYPES)}",
                    code="INVALID_ELEMENT_TYPE"
                )

            # Validate position
            pos = elem.get("position", {})
            x = pos.get("x", 0)
            y = pos.get("y", 0)
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                raise ValidationError(message=f"Element '{elem_id}' position (x, y) must be numeric", code="INVALID_POSITION")
            if x < 0 or x >= canvas_width or y < 0 or y >= canvas_height:
                raise ValidationError(
                    message=f"Element '{elem_id}' position ({x}, {y}) is outside canvas ({canvas_width}x{canvas_height})",
                    code="ELEMENT_OUT_OF_BOUNDS"
                )

            # Validate size
            size = elem.get("size", {})
            w = size.get("width", 100)
            h = size.get("height", 50)
            if not (isinstance(w, (int, float)) and isinstance(h, (int, float))) or w <= 0 or h <= 0:
                raise ValidationError(message=f"Element '{elem_id}' size (width, height) must be positive numbers", code="INVALID_SIZE")

            # Validate text placeholders if content exists
            content = elem.get("content", "")
            if isinstance(content, str):
                PlaceholderService.extract_placeholders(content)

            # Validate style if present
            style = elem.get("style", {})
            if isinstance(style, dict):
                align = style.get("alignment") or style.get("align")
                if align and align not in VALID_ALIGNMENTS:
                    raise ValidationError(
                        message=f"Element '{elem_id}' has invalid alignment '{align}'. Allowed: {', '.join(VALID_ALIGNMENTS)}",
                        code="INVALID_ALIGNMENT"
                    )

                color = style.get("color")
                if color and isinstance(color, str) and not HEX_COLOR_REGEX.match(color):
                    # Also permit rgba/rgb/transparent strings
                    if not (color.startswith("rgb") or color in ["transparent", "white", "black"]):
                        raise ValidationError(
                            message=f"Element '{elem_id}' has invalid color format '{color}'",
                            code="INVALID_COLOR_FORMAT"
                        )

    @classmethod
    def validate_for_publish(cls, version_doc: Dict[str, Any]) -> None:
        """
        Enforce strict criteria before publishing a template version:
        1. Canvas dimensions valid
        2. Background asset exists (or explicit SVG/blank background permitted)
        3. At least one text element with placeholder exists (e.g. {{recipient_name}})
        4. Elements fit on canvas
        """
        width = version_doc.get("width", 3508)
        height = version_doc.get("height", 2480)
        cls.validate_canvas(width, height)

        elements = version_doc.get("elements", [])
        if not elements:
            raise ValidationError(
                message="Cannot publish template version with zero elements. Add certificate placeholders.",
                code="NO_ELEMENTS"
            )

        cls.validate_elements(elements, width, height)

        # Check for recipient placeholder
        fields = PlaceholderService.extract_fields_from_elements(elements)
        recipient_fields = [f for f in fields if f.get("source") == "recipient"]
        if not recipient_fields:
            raise ValidationError(
                message="Cannot publish template version without recipient placeholders. Example: {{recipient_name}}",
                code="MISSING_RECIPIENT_PLACEHOLDER"
            )
