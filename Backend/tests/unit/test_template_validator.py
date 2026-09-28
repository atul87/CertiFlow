import pytest
from app.core.exceptions import ValidationError
from app.services.template_validator import TemplateValidator


def test_canvas_validation():
    # Valid
    TemplateValidator.validate_canvas(3508, 2480)

    # Invalid: Too small
    with pytest.raises(ValidationError):
        TemplateValidator.validate_canvas(100, 2480)

    # Invalid: Too large
    with pytest.raises(ValidationError):
        TemplateValidator.validate_canvas(3508, 25000)


def test_elements_bounds_and_duplicate_id():
    canvas_w = 3508
    canvas_h = 2480

    # Valid
    valid_elems = [
        {"id": "el1", "type": "text", "position": {"x": 500, "y": 500}, "size": {"width": 800, "height": 100}},
        {"id": "el2", "type": "qr", "position": {"x": 100, "y": 100}, "size": {"width": 200, "height": 200}}
    ]
    TemplateValidator.validate_elements(valid_elems, canvas_w, canvas_h)

    # Duplicate ID
    dup_elems = [
        {"id": "el1", "type": "text", "position": {"x": 100, "y": 100}, "size": {"width": 200, "height": 50}},
        {"id": "el1", "type": "text", "position": {"x": 300, "y": 300}, "size": {"width": 200, "height": 50}}
    ]
    with pytest.raises(ValidationError):
        TemplateValidator.validate_elements(dup_elems, canvas_w, canvas_h)

    # Out of bounds position
    oob_elems = [
        {"id": "el1", "type": "text", "position": {"x": 4000, "y": 100}, "size": {"width": 200, "height": 50}}
    ]
    with pytest.raises(ValidationError):
        TemplateValidator.validate_elements(oob_elems, canvas_w, canvas_h)


def test_validate_for_publish():
    # Fails if 0 elements
    with pytest.raises(ValidationError):
        TemplateValidator.validate_for_publish({
            "width": 3508,
            "height": 2480,
            "elements": []
        })

    # Fails if no recipient placeholder
    with pytest.raises(ValidationError):
        TemplateValidator.validate_for_publish({
            "width": 3508,
            "height": 2480,
            "elements": [
                {"id": "t1", "type": "text", "content": "Just fixed text without placeholders", "position": {"x": 100, "y": 100}, "size": {"width": 200, "height": 50}}
            ]
        })

    # Passes when recipient placeholder is present
    TemplateValidator.validate_for_publish({
        "width": 3508,
        "height": 2480,
        "elements": [
            {"id": "t1", "type": "text", "content": "{{recipient_name}}", "position": {"x": 100, "y": 100}, "size": {"width": 200, "height": 50}}
        ]
    })
