from app.services.validation_service import ValidationService


def test_validate_row_success():
    raw_row = {
        "Name": "Atul Kumar",
        "Email": "atul@example.com",
        "Date": "2026-09-28"
    }
    mappings = [
        {"source_column": "Name", "target_field": "recipient_name"},
        {"source_column": "Email", "target_field": "recipient_email"},
        {"source_column": "Date", "target_field": "issue_date"}
    ]
    template_fields = [
        {"key": "recipient_name", "required": True, "type": "text"},
        {"key": "recipient_email", "required": True, "type": "email"},
        {"key": "issue_date", "required": True, "type": "date"}
    ]

    res = ValidationService.validate_row(1, raw_row, mappings, template_fields)
    assert res["status"] == "valid"
    assert len(res["errors"]) == 0
    assert res["data"]["recipient_name"] == "Atul Kumar"
    assert res["data"]["recipient_email"] == "atul@example.com"
    assert res["data"]["issue_date"] == "2026-09-28"


def test_validate_row_missing_name_and_invalid_email():
    raw_row = {
        "Name": "   ",  # Missing / blank
        "Email": "not-an-email"
    }
    mappings = [
        {"source_column": "Name", "target_field": "recipient_name"},
        {"source_column": "Email", "target_field": "recipient_email"}
    ]
    template_fields = [
        {"key": "recipient_name", "required": True, "type": "text"},
        {"key": "recipient_email", "required": True, "type": "email"}
    ]

    res = ValidationService.validate_row(2, raw_row, mappings, template_fields)
    assert res["status"] == "error"
    codes = [e["code"] for e in res["errors"]]
    assert "MISSING_REQUIRED_FIELD" in codes
    assert "INVALID_EMAIL" in codes


def test_validate_row_long_name_warning():
    raw_row = {
        "Name": "Her Royal Highness Princess Maria-Theresia von Hohenzollern-Sigmaringen",
        "Email": "maria@example.com"
    }
    mappings = [
        {"source_column": "Name", "target_field": "recipient_name"},
        {"source_column": "Email", "target_field": "recipient_email"}
    ]
    template_fields = [
        {"key": "recipient_name", "required": True, "type": "text"},
        {"key": "recipient_email", "required": True, "type": "email"}
    ]

    res = ValidationService.validate_row(3, raw_row, mappings, template_fields)
    assert res["status"] == "warning"
    assert len(res["errors"]) == 0
    w_codes = [w["code"] for w in res["warnings"]]
    assert "LONG_RECIPIENT_NAME" in w_codes


def test_flag_dataset_duplicates():
    dataset = [
        {"data": {"recipient_email": "alice@example.com"}, "warnings": [], "status": "valid"},
        {"data": {"recipient_email": "bob@example.com"}, "warnings": [], "status": "valid"},
        {"data": {"recipient_email": "alice@example.com"}, "warnings": [], "status": "valid"}
    ]
    ValidationService.flag_dataset_duplicates(dataset)

    # Alice rows should have warning
    assert dataset[0]["status"] == "warning"
    assert dataset[0]["warnings"][0]["code"] == "DUPLICATE_RECIPIENT"
    assert dataset[2]["status"] == "warning"
    assert dataset[2]["warnings"][0]["code"] == "DUPLICATE_RECIPIENT"

    # Bob row remains valid
    assert dataset[1]["status"] == "valid"
    assert len(dataset[1]["warnings"]) == 0
