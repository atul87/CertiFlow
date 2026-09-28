import re
from typing import List, Dict, Any, Set, Tuple
from app.core.exceptions import ValidationError

# Valid placeholder regex: {{valid_variable_name}}
PLACEHOLDER_REGEX = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")
# Regex to detect malformed or spaces within braces: e.g. {{ invalid name }} or {{{extra}}}
MALFORMED_REGEX = re.compile(r"\{\{[^}]*\s+[^}]*\}\}|\{\{\{[^}]+\}\}\}")

SYSTEM_FIELDS: Dict[str, Dict[str, Any]] = {
    "certificate_id": {
        "key": "certificate_id",
        "label": "Certificate ID",
        "type": "text",
        "required": False,
        "source": "system",
        "description": "Unique system-generated certificate credential identifier"
    },
    "verification_code": {
        "key": "verification_code",
        "label": "Verification Code",
        "type": "text",
        "required": False,
        "source": "system",
        "description": "Cryptographic or short alphanumeric verification code"
    },
    "verification_url": {
        "key": "verification_url",
        "label": "Verification URL",
        "type": "url",
        "required": False,
        "source": "system",
        "description": "Full public verification web URL for QR code or link"
    },
    "issued_at": {
        "key": "issued_at",
        "label": "Issue Date",
        "type": "date",
        "required": False,
        "source": "system",
        "description": "System issuance timestamp"
    }
}

SAMPLE_VALUES: Dict[str, str] = {
    "recipient_name": "Atul Sharma",
    "program_name": "Advanced Artificial Intelligence & Deep Learning",
    "issue_date": "28 September 2026",
    "issuer_name": "Prof. R. K. Verma",
    "issuer_title": "Head of Academic Affairs",
    "organization_name": "Allenhouse Institute of Technology",
    "certificate_id": "CERT-2026-984210",
    "verification_code": "9F8A-77B2-C4",
    "verification_url": "https://verify.certiflow.io/cert/CERT-2026-984210",
    "issued_at": "2026-09-28",
    "grade": "Distinction",
    "hours": "48 Hours"
}


class PlaceholderService:
    @classmethod
    def extract_placeholders(cls, text: str) -> List[str]:
        """
        Extract unique placeholder keys from a text string.
        Validates syntax; raises ValidationError if invalid or malformed brackets found.
        """
        if not text or not isinstance(text, str):
            return []

        # Check for malformed placeholders
        if MALFORMED_REGEX.search(text):
            raise ValidationError(
                message=f"Malformed placeholder syntax in text: '{text}'. Expected format: '{{{{variable_name}}}}'",
                code="INVALID_PLACEHOLDER_SYNTAX"
            )

        # Check for unmatched or partially unclosed double braces
        open_count = text.count("{{")
        close_count = text.count("}}")
        if open_count != close_count:
            raise ValidationError(
                message=f"Unmatched placeholder braces in text: '{text}'",
                code="UNMATCHED_PLACEHOLDER_BRACES"
            )

        matches = PLACEHOLDER_REGEX.findall(text)
        return list(dict.fromkeys(matches))  # Preserve order, unique

    @classmethod
    def extract_fields_from_elements(cls, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan all elements (text, qr, image) for placeholders and return
        structured logical field definitions.
        Duplicates are automatically consolidated.
        """
        keys_found: Set[str] = set()
        fields: List[Dict[str, Any]] = []

        for elem in elements:
            elem_type = elem.get("type", "text")
            content = elem.get("content", "")

            # Text or QR elements can contain placeholders
            if isinstance(content, str) and "{{" in content:
                found = cls.extract_placeholders(content)
                for key in found:
                    if key not in keys_found:
                        keys_found.add(key)
                        if key in SYSTEM_FIELDS:
                            fields.append(dict(SYSTEM_FIELDS[key]))
                        else:
                            # User recipient field
                            formatted_label = key.replace("_", " ").title()
                            field_type = "date" if "date" in key else "text"
                            fields.append({
                                "key": key,
                                "label": formatted_label,
                                "type": field_type,
                                "required": True,
                                "source": "recipient",
                                "description": f"Recipient data field: {formatted_label}"
                            })

        return fields

    @classmethod
    def substitute_text(
        cls,
        text: str,
        data: Dict[str, Any],
        use_sample_fallback: bool = False
    ) -> str:
        """
        Substitute {{key}} placeholders in text with provided data or sample values.
        """
        if not text or "{{" not in text:
            return text

        def replacer(match):
            key = match.group(1)
            if key in data and data[key] is not None:
                return str(data[key])
            if use_sample_fallback:
                return SAMPLE_VALUES.get(key, f"[{key.replace('_', ' ').title()}]")
            return ""

        return PLACEHOLDER_REGEX.sub(replacer, text)
