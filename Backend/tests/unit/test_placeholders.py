import pytest
from app.core.exceptions import ValidationError
from app.services.placeholder_service import PlaceholderService


def test_extract_valid_placeholders():
    text = "Presented to {{recipient_name}} for completing {{course_name}} on {{completion_date}}."
    placeholders = PlaceholderService.extract_placeholders(text)
    assert placeholders == ["recipient_name", "course_name", "completion_date"]


def test_reject_malformed_placeholders():
    # Placeholder with whitespace inside
    with pytest.raises(ValidationError):
        PlaceholderService.extract_placeholders("Hello {{recipient name}}")

    # Triple braces
    with pytest.raises(ValidationError):
        PlaceholderService.extract_placeholders("Hello {{{recipient_name}}}")

    # Unmatched braces
    with pytest.raises(ValidationError):
        PlaceholderService.extract_placeholders("Hello {{recipient_name")


def test_duplicate_placeholders_consolidation():
    elements = [
        {"id": "t1", "type": "text", "content": "Awarded to {{recipient_name}}"},
        {"id": "t2", "type": "text", "content": "Congratulations {{recipient_name}} on your achievement in {{program_name}}!"}
    ]
    fields = PlaceholderService.extract_fields_from_elements(elements)

    # Must extract only 2 unique logical fields
    keys = [f["key"] for f in fields]
    assert keys == ["recipient_name", "program_name"]

    # recipient_name should be recipient source, required
    recip = next(f for f in fields if f["key"] == "recipient_name")
    assert recip["source"] == "recipient"
    assert recip["required"] is True


def test_system_fields_classification():
    elements = [
        {"id": "t1", "type": "text", "content": "Cert ID: {{certificate_id}}"},
        {"id": "t2", "type": "qr", "content": "{{verification_url}}"}
    ]
    fields = PlaceholderService.extract_fields_from_elements(elements)
    assert len(fields) == 2

    cert_id_field = next(f for f in fields if f["key"] == "certificate_id")
    assert cert_id_field["source"] == "system"
    assert cert_id_field["required"] is False

    qr_field = next(f for f in fields if f["key"] == "verification_url")
    assert qr_field["source"] == "system"
    assert qr_field["type"] == "url"


def test_substitute_text():
    template_str = "Hi {{recipient_name}}, your code is {{verification_code}}."

    # Explicit data
    res1 = PlaceholderService.substitute_text(template_str, {
        "recipient_name": "Atul Sharma",
        "verification_code": "SEC-999"
    })
    assert res1 == "Hi Atul Sharma, your code is SEC-999."

    # Sample fallback for missing keys
    res2 = PlaceholderService.substitute_text(template_str, {}, use_sample_fallback=True)
    assert "Atul Sharma" in res2
    assert "9F8A-77B2-C4" in res2
