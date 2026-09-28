from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that applies production security headers to all HTTP responses.
    Protects against MIME sniffing, clickjacking, XSS, and unencrypted transport.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        if not settings.ENABLE_SECURITY_HEADERS:
            return response

        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent framing / clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disable sensitive browser capabilities
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"

        # Enforce HTTPS in production
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Default Content Security Policy
        # Safe defaults allowing self, data URLs, fonts from Google/self, and inline styles for preview rendering
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: blob: https:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline'; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response
