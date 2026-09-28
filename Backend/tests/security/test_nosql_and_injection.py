import pytest
from app.security.nosql_sanitizer import NoSQLSanitizer
from app.core.exceptions import ValidationError


def test_nosql_injection_detection_operators():
    # Dangerous MongoDB query operators in untrusted user input
    bad_inputs = [
        {"username": {"$gt": ""}},
        {"status": {"$ne": "revoked"}},
        {"$where": "this.password.length > 0"},
        {"role": {"$regex": "^admin"}},
        {"nested": {"filters": [{"$expr": {"$eq": [1, 1]}}]}},
    ]

    for item in bad_inputs:
        with pytest.raises(ValidationError) as exc:
            NoSQLSanitizer.validate_no_injection(item)
        assert exc.value.code == "NOSQL_INJECTION_DETECTED"


def test_nosql_injection_dot_notation_detection():
    # Dot notation traversal into internal/privileged fields
    bad_dict = {"metadata.is_admin": True}
    with pytest.raises(ValidationError) as exc:
        NoSQLSanitizer.validate_no_injection(bad_dict, allow_dots=False)
    assert exc.value.code == "NOSQL_INJECTION_DETECTED"

    # Permitted when explicitly allow_dots=True
    NoSQLSanitizer.validate_no_injection(bad_dict, allow_dots=True)


def test_nosql_sanitizer_cleans_operators():
    untrusted = {
        "name": "CertiFlow Corp",
        "$where": "evil()",
        "settings": {
            "$gt": 10,
            "theme": "dark",
            "tags": ["prod", {"$regex": ".*"}, "verified"]
        }
    }

    sanitized = NoSQLSanitizer.sanitize(untrusted)
    assert "$where" not in sanitized
    assert "$gt" not in sanitized["settings"]
    assert sanitized["name"] == "CertiFlow Corp"
    assert sanitized["settings"]["theme"] == "dark"
    assert sanitized["settings"]["tags"] == ["prod", {}, "verified"]


def test_safe_input_passes_validation():
    safe_data = {
        "name": "Spring Hackathon 2026",
        "recipient": {
            "name": "Jane Doe",
            "email": "jane@example.com"
        },
        "tags": ["hackathon", "award", "first-place"]
    }
    NoSQLSanitizer.validate_no_injection(safe_data)
