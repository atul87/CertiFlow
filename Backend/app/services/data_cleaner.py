import re
from typing import Any, Optional

NULL_EQUIVALENTS = {"null", "n/a", "na", "-", "--", "none", "nan", "nil", "undefined"}


class DataCleaner:
    @classmethod
    def clean_text(cls, val: Any) -> Optional[str]:
        """Strip whitespace and convert common null representations to None."""
        if val is None:
            return None

        s = str(val).strip()
        if not s or s.lower() in NULL_EQUIVALENTS:
            return None

        # Collapse excessive internal spaces
        return re.sub(r"\s+", " ", s)

    @classmethod
    def clean_email(cls, val: Any) -> Optional[str]:
        cleaned = cls.clean_text(val)
        if not cleaned:
            return None
        return cleaned.lower()

    @classmethod
    def clean_name(cls, val: Any) -> Optional[str]:
        """Preserve case while removing surrounding and excessive whitespace."""
        return cls.clean_text(val)
