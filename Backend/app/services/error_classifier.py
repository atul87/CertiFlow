from __future__ import annotations
from enum import Enum
from typing import Dict, Any


class ErrorCategory(str, Enum):
    RETRYABLE = "retryable"
    PERMANENT = "permanent"


# Error codes that are known to be permanent
PERMANENT_ERROR_CODES = {
    "MISSING_REQUIRED_FIELD",
    "INVALID_RECIPIENT_DATA",
    "FONT_NOT_FOUND",
    "MISSING_FONT",
    "TEMPLATE_NOT_FOUND",
    "TEMPLATE_NOT_PUBLISHED",
    "TEMPLATE_VERSION_NOT_FOUND",
    "PERMISSION_DENIED",
    "UNAUTHORIZED",
    "INVALID_DATE",
    "INVALID_IMAGE_DATA",
}

# Error codes that are known to be retryable
RETRYABLE_ERROR_CODES = {
    "STORAGE_TIMEOUT",
    "STORAGE_ERROR",
    "REDIS_TIMEOUT",
    "CONNECTION_ERROR",
    "RENDERER_CRASH",
    "MEMORY_ERROR",
    "DATABASE_TIMEOUT",
    "NETWORK_ERROR",
    "WORKER_TIMEOUT",
}


class ErrorClassifier:
    @staticmethod
    def classify(code: str, message: str = "") -> ErrorCategory:
        """Classify an error into RETRYABLE or PERMANENT."""
        normalized_code = (code or "").upper().strip()

        if normalized_code in PERMANENT_ERROR_CODES:
            return ErrorCategory.PERMANENT

        if normalized_code in RETRYABLE_ERROR_CODES:
            return ErrorCategory.RETRYABLE

        # Keyword heuristics on error message
        msg_lower = (message or "").lower()
        if any(term in msg_lower for term in ["timeout", "connection refused", "reset by peer", "temporarily unavailable"]):
            return ErrorCategory.RETRYABLE

        if any(term in msg_lower for term in ["missing required", "not found", "cannot parse", "syntax error"]):
            return ErrorCategory.PERMANENT

        # Default fallback: if unknown, treat as retryable once up to max_attempts
        return ErrorCategory.RETRYABLE

    @staticmethod
    def is_retryable(code: str, message: str = "") -> bool:
        return ErrorClassifier.classify(code, message) == ErrorCategory.RETRYABLE
