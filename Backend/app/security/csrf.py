import hmac
import secrets
from typing import Optional
from fastapi import Request
from app.core.config import settings
from app.core.exceptions import ForbiddenError

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def generate_csrf_token() -> str:
    """Generate a cryptographically secure URL-safe CSRF token."""
    return secrets.token_urlsafe(32)


def validate_csrf_token(request: Request) -> None:
    """
    Validate CSRF token for state-mutating requests (POST, PUT, PATCH, DELETE)
    when authenticated via cookies.
    
    Checks that the X-CSRF-Token header matches the cookie token.
    Raises ForbiddenError if validation fails.
    """
    if request.method in SAFE_METHODS:
        return

    csrf_cookie = request.cookies.get(settings.COOKIE_CSRF_NAME)
    csrf_header = request.headers.get("X-CSRF-Token") or request.headers.get("x-csrf-token")

    if not csrf_cookie or not csrf_header:
        raise ForbiddenError(
            message="CSRF validation failed: missing CSRF token header or cookie",
            code="CSRF_TOKEN_MISSING"
        )

    if not hmac.compare_digest(csrf_cookie, csrf_header):
        raise ForbiddenError(
            message="CSRF validation failed: token mismatch",
            code="CSRF_TOKEN_MISMATCH"
        )
