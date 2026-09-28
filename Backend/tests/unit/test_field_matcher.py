from app.services.field_matcher import FieldMatcher


def test_exact_and_normalized_matching():
    # Exact match
    score, method = FieldMatcher.match_column_to_field("recipient_name", "string", "recipient_name")
    assert score == 1.0
    assert method == "exact"

    # Normalized match (spaces/casing)
    score, method = FieldMatcher.match_column_to_field("Recipient Name", "string", "recipient_name")
    assert score >= 0.95
    assert method in ["normalized", "synonym"]


def test_synonym_matching():
    # Student Name -> recipient_name
    score, method = FieldMatcher.match_column_to_field("Student Name", "string", "recipient_name")
    assert score >= 0.90
    assert method == "synonym"

    # Email Address -> recipient_email
    score, method = FieldMatcher.match_column_to_field("Email Address", "email", "recipient_email")
    assert score >= 0.90
    assert method in ["synonym", "data_type"]

    # Course -> program_name
    score, method = FieldMatcher.match_column_to_field("Course", "string", "program_name")
    assert score >= 0.90
    assert method == "synonym"

    # Completion Date -> issue_date
    score, method = FieldMatcher.match_column_to_field("Completion Date", "date", "issue_date")
    assert score >= 0.90
    assert method in ["synonym", "data_type"]


def test_suggest_mappings_pipeline():
    columns = ["Full Name", "Student Email", "Workshop Track", "Date Awarded", "Random Code"]
    profiles = [
        {"name": "Full Name", "detected_type": "string"},
        {"name": "Student Email", "detected_type": "email"},
        {"name": "Workshop Track", "detected_type": "string"},
        {"name": "Date Awarded", "detected_type": "date"},
        {"name": "Random Code", "detected_type": "string"}
    ]
    template_fields = [
        {"key": "recipient_name", "label": "Recipient Name", "required": True, "source": "recipient"},
        {"key": "recipient_email", "label": "Recipient Email", "required": True, "source": "recipient"},
        {"key": "program_name", "label": "Program Name", "required": True, "source": "recipient"},
        {"key": "issue_date", "label": "Issue Date", "required": True, "source": "recipient"},
        {"key": "certificate_id", "label": "Certificate ID", "required": False, "source": "system"}
    ]

    suggestions = FieldMatcher.suggest_mappings(columns, profiles, template_fields)
    sug_dict = {s["target_field"]: s["source_column"] for s in suggestions}

    assert sug_dict["recipient_name"] == "Full Name"
    assert sug_dict["recipient_email"] == "Student Email"
    assert sug_dict["program_name"] == "Workshop Track"
    assert sug_dict["issue_date"] == "Date Awarded"
    # System fields should not be matched to CSV columns
    assert "certificate_id" not in sug_dict
