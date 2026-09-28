import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set
from dateutil import parser as date_parser
from app.services.data_cleaner import DataCleaner

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ValidationService:
    @classmethod
    def normalize_date_string(cls, date_str: str, dayfirst: bool = True) -> Tuple[Optional[str], bool, Optional[str]]:
        """
        Normalize date string to YYYY-MM-DD.
        Returns: (normalized_date_or_none, is_ambiguous, error_message_if_any)
        """
        if not date_str:
            return None, False, None

        # Check for ambiguity: e.g. 01/02/2026 or 05-06-2026
        is_ambiguous = False
        parts = re.split(r"[/.-]", date_str.strip())
        if len(parts) >= 2 and len(parts[0]) <= 2 and len(parts[1]) <= 2:
            try:
                p1, p2 = int(parts[0]), int(parts[1])
                if 1 <= p1 <= 12 and 1 <= p2 <= 12 and p1 != p2:
                    is_ambiguous = True
            except ValueError:
                pass

        try:
            parsed = date_parser.parse(date_str, dayfirst=dayfirst)
            return parsed.strftime("%Y-%m-%d"), is_ambiguous, None
        except (ValueError, TypeError, OverflowError) as e:
            return None, False, f"Could not parse date '{date_str}': {str(e)}"

    @classmethod
    def validate_row(
        cls,
        row_number: int,
        raw_row: Dict[str, Any],
        mappings: List[Dict[str, Any]],
        template_fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate and normalize a single row based on established column mappings and template fields.
        """
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        normalized_data: Dict[str, Any] = {}

        field_def_map = {f["key"]: f for f in template_fields}
        mapped_targets: Set[str] = set()

        for m in mappings:
            src_col = m.get("source_column")
            target_field = m.get("target_field")
            if not target_field or not src_col:
                continue

            mapped_targets.add(target_field)
            raw_val = raw_row.get(src_col)
            fdef = field_def_map.get(target_field, {})
            is_required = fdef.get("required", True)
            field_type = fdef.get("type", "text")

            cleaned_val = DataCleaner.clean_text(raw_val)

            if cleaned_val is None:
                if is_required:
                    errors.append({
                        "field": target_field,
                        "code": "MISSING_REQUIRED_FIELD",
                        "message": f"Required field '{fdef.get('label', target_field)}' is missing or empty",
                        "severity": "ERROR"
                    })
                normalized_data[target_field] = None
                continue

            # Field-specific validation & normalization
            if target_field == "recipient_email" or field_type == "email":
                email_clean = DataCleaner.clean_email(cleaned_val)
                if not EMAIL_REGEX.match(email_clean or ""):
                    errors.append({
                        "field": target_field,
                        "code": "INVALID_EMAIL",
                        "message": f"Invalid email format: '{cleaned_val}'",
                        "severity": "ERROR"
                    })
                normalized_data[target_field] = email_clean

            elif target_field == "recipient_name":
                name_clean = DataCleaner.clean_name(cleaned_val)
                if len(name_clean) > 35:
                    warnings.append({
                        "field": target_field,
                        "code": "LONG_RECIPIENT_NAME",
                        "message": f"Long recipient name ({len(name_clean)} chars). Smart-fit text scaling will be applied.",
                        "severity": "WARNING"
                    })
                normalized_data[target_field] = name_clean

            elif target_field == "issue_date" or field_type == "date":
                norm_date, is_ambig, err_msg = cls.normalize_date_string(cleaned_val)
                if err_msg:
                    errors.append({
                        "field": target_field,
                        "code": "INVALID_DATE_FORMAT",
                        "message": err_msg,
                        "severity": "ERROR"
                    })
                    normalized_data[target_field] = cleaned_val
                else:
                    if is_ambig:
                        warnings.append({
                            "field": target_field,
                            "code": "AMBIGUOUS_DATE_FORMAT",
                            "message": f"Ambiguous date '{cleaned_val}' parsed as {norm_date}",
                            "severity": "WARNING"
                        })
                    normalized_data[target_field] = norm_date

            else:
                normalized_data[target_field] = cleaned_val

        # Check for unmapped required template fields
        for f in template_fields:
            k = f["key"]
            if f.get("source") != "system" and f.get("required", True) and k not in mapped_targets:
                errors.append({
                    "field": k,
                    "code": "UNMAPPED_REQUIRED_FIELD",
                    "message": f"Required template field '{f.get('label', k)}' has not been mapped",
                    "severity": "ERROR"
                })

        # Determine overall row status
        if errors:
            status = "error"
        elif warnings:
            status = "warning"
        else:
            status = "valid"

        return {
            "row_number": row_number,
            "raw_data": raw_row,
            "data": normalized_data,
            "status": status,
            "errors": errors,
            "warnings": warnings
        }

    @classmethod
    def flag_dataset_duplicates(cls, validated_rows: List[Dict[str, Any]]) -> None:
        """
        Flag duplicate recipients across the dataset with WARNING (without dropping rows).
        """
        email_counts: Dict[str, int] = {}
        for r in validated_rows:
            email = r.get("data", {}).get("recipient_email")
            if email:
                email_counts[email] = email_counts.get(email, 0) + 1

        for r in validated_rows:
            email = r.get("data", {}).get("recipient_email")
            if email and email_counts.get(email, 0) > 1:
                r["warnings"].append({
                    "field": "recipient_email",
                    "code": "DUPLICATE_RECIPIENT",
                    "message": f"Duplicate email address '{email}' appears {email_counts[email]} times in dataset",
                    "severity": "WARNING"
                })
                if r["status"] == "valid":
                    r["status"] = "warning"
