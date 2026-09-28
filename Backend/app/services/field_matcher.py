import re
import difflib
from typing import List, Dict, Any, Optional, Tuple

SYNONYM_DICTIONARY: Dict[str, List[str]] = {
    "recipient_name": [
        "name", "full name", "fullname", "student name", "candidate name",
        "participant name", "recipient name", "employee name", "recipient",
        "participant", "candidate", "attendee", "student", "member name"
    ],
    "recipient_email": [
        "email", "email address", "e-mail", "mail", "recipient email",
        "student email", "participant email", "candidate email", "mail id",
        "email id", "contact email"
    ],
    "program_name": [
        "course", "program", "training", "workshop", "event", "course name",
        "program name", "workshop name", "event name", "track", "bootcamp",
        "subject", "degree", "diploma"
    ],
    "issue_date": [
        "date", "completion date", "issue date", "issued date",
        "certificate date", "completion_date", "award date", "awarded date",
        "event date", "date of issue", "completion"
    ],
    "issuer_name": [
        "issuer", "issuer name", "signed by", "signatory", "instructor",
        "director", "coordinator", "professor", "authorized by", "signature"
    ],
    "issuer_title": [
        "issuer title", "signatory title", "designation", "title", "role", "position"
    ],
    "grade": [
        "grade", "score", "marks", "percentage", "performance", "result", "cgpa", "gpa"
    ],
    "certificate_id": [
        "certificate id", "cert id", "credential id", "cert number",
        "certificate number", "serial number"
    ]
}


def normalize_string(s: str) -> str:
    """Normalize string: lowercase, remove punctuation, spaces, and separators."""
    if not s:
        return ""
    return re.sub(r"[^a-z0-9]", "", s.lower())


class FieldMatcher:
    @classmethod
    def match_column_to_field(
        cls,
        column_name: str,
        detected_type: str,
        target_field: str
    ) -> Tuple[float, str]:
        """
        Calculates confidence score [0.0 - 1.0] and method for matching column to target field.
        """
        norm_col = normalize_string(column_name)
        norm_target = normalize_string(target_field)

        # 1. Exact Match (100%)
        if column_name.lower().strip() == target_field.lower().strip():
            return 1.0, "exact"

        # 2. Normalized Exact Match (98%)
        if norm_col == norm_target:
            return 0.98, "normalized"

        # 3. Synonym Match (95%)
        synonyms = SYNONYM_DICTIONARY.get(target_field, [])
        for syn in synonyms:
            if normalize_string(syn) == norm_col:
                return 0.95, "synonym"
            # Partial substring containment in synonym: e.g. "student name" in "student full name"
            if syn in column_name.lower():
                return 0.90, "synonym"

        # 4. Data Type Match (85% - 90%)
        if detected_type == "email" and "email" in target_field:
            return 0.92, "data_type"
        if detected_type == "date" and ("date" in target_field or "issued" in target_field):
            return 0.88, "data_type"

        # 5. Fuzzy Match (Levenshtein ratio)
        similarity = difflib.SequenceMatcher(None, norm_col, norm_target).ratio()
        if similarity >= 0.70:
            return round(similarity * 0.9, 2), "fuzzy"

        return 0.0, "none"

    @classmethod
    def suggest_mappings(
        cls,
        columns: List[str],
        column_profiles: List[Dict[str, Any]],
        template_fields: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal mapping pairs between CSV columns and template fields.
        """
        type_map = {p["name"]: p.get("detected_type", "string") for p in column_profiles}
        suggestions: List[Dict[str, Any]] = []
        mapped_columns = set()

        # Sort template fields: required fields first
        sorted_fields = sorted(template_fields, key=lambda f: not f.get("required", True))

        for f in sorted_fields:
            field_key = f["key"]
            source = f.get("source", "recipient")

            # System fields (certificate_id, verification_url, etc.) don't require CSV column mapping
            if source == "system":
                continue

            best_col: Optional[str] = None
            best_score = 0.0
            best_method = "none"

            for col in columns:
                if col in mapped_columns:
                    continue

                col_type = type_map.get(col, "string")
                score, method = cls.match_column_to_field(col, col_type, field_key)

                if score > best_score:
                    best_score = score
                    best_col = col
                    best_method = method

            if best_col and best_score >= 0.60:
                mapped_columns.add(best_col)
                conf_level = "high" if best_score >= 0.90 else ("medium" if best_score >= 0.70 else "low")
                suggestions.append({
                    "source_column": best_col,
                    "target_field": field_key,
                    "target_label": f.get("label", field_key.replace("_", " ").title()),
                    "confidence": best_score,
                    "confidence_level": conf_level,
                    "method": best_method,
                    "required": f.get("required", True)
                })
            else:
                # Unmapped field
                suggestions.append({
                    "source_column": None,
                    "target_field": field_key,
                    "target_label": f.get("label", field_key.replace("_", " ").title()),
                    "confidence": 0.0,
                    "confidence_level": "unmapped",
                    "method": "none",
                    "required": f.get("required", True)
                })

        return suggestions
