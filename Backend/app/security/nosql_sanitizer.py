"""
NoSQL Injection Sanitizer & Guard for MongoDB.
Detects, rejects, and sanitizes untrusted input containing MongoDB operators
(keys starting with '$' or containing unauthorized dot notation traversal).
"""
from typing import Any, Dict, List, Union
from app.core.exceptions import ValidationError


class NoSQLSanitizer:
    FORBIDDEN_OPERATORS = {
        "$where", "$regex", "$gt", "$gte", "$lt", "$lte", "$ne", "$in", "$nin",
        "$or", "$and", "$not", "$nor", "$exists", "$type", "$mod", "$text",
        "$expr", "$jsonSchema", "$lookup", "$graphLookup", "$group", "$project",
        "$match", "$unwind", "$facet", "$bucket", "$bucketAuto"
    }

    @classmethod
    def validate_no_injection(cls, data: Any, allow_dots: bool = False, depth: int = 0) -> None:
        """
        Recursively checks data structures for keys starting with '$' or containing '.' (if allow_dots=False).
        Raises ValidationError if any MongoDB operator or injection vector is detected.
        """
        if depth > 20:
            raise ValidationError(
                message="Input nesting level exceeds maximum allowable depth",
                code="INPUT_NESTING_TOO_DEEP"
            )

        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(key, str):
                    continue
                # Block any operator key starting with $
                if key.startswith("$") or key.lower() in cls.FORBIDDEN_OPERATORS:
                    raise ValidationError(
                        message=f"Disallowed query operator detected: '{key}'",
                        code="NOSQL_INJECTION_DETECTED"
                    )
                # Block dot notation if not explicitly permitted
                if not allow_dots and "." in key:
                    raise ValidationError(
                        message=f"Disallowed dot notation in query parameter: '{key}'",
                        code="NOSQL_INJECTION_DETECTED"
                    )
                cls.validate_no_injection(value, allow_dots=allow_dots, depth=depth + 1)

        elif isinstance(data, list):
            for item in data:
                cls.validate_no_injection(item, allow_dots=allow_dots, depth=depth + 1)

    @classmethod
    def sanitize(cls, data: Any, allow_dots: bool = False, depth: int = 0) -> Any:
        """
        Recursively strips any dictionary keys starting with '$' or containing '.' (if allow_dots=False).
        Returns a clean copy of the data without forbidden operators.
        """
        if depth > 20:
            return data

        if isinstance(data, dict):
            clean_dict = {}
            for key, value in data.items():
                if isinstance(key, str):
                    if key.startswith("$") or key.lower() in cls.FORBIDDEN_OPERATORS:
                        continue
                    if not allow_dots and "." in key:
                        continue
                clean_dict[key] = cls.sanitize(value, allow_dots=allow_dots, depth=depth + 1)
            return clean_dict

        elif isinstance(data, list):
            return [cls.sanitize(item, allow_dots=allow_dots, depth=depth + 1) for item in data]

        return data
