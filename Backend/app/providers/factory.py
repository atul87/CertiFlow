from __future__ import annotations
from typing import Optional, Dict, Any
from app.core.config import settings
from app.providers.base import EmailProvider
from app.providers.mock import MockEmailProvider
from app.providers.smtp import SMTPEmailProvider


def get_email_provider(org_settings: Optional[Dict[str, Any]] = None) -> EmailProvider:
    """
    Factory returning the configured EmailProvider.
    Uses organization-level settings if provided, otherwise falls back to system config.
    """
    provider_name = (org_settings.get("provider") if org_settings else None) or settings.EMAIL_PROVIDER
    provider_name = provider_name.lower().strip()

    if provider_name == "smtp":
        host = (org_settings.get("smtp_host") if org_settings else None) or "localhost"
        port = (org_settings.get("smtp_port") if org_settings else None) or 587
        username = org_settings.get("smtp_username") if org_settings else None
        password = org_settings.get("smtp_password") if org_settings else None
        return SMTPEmailProvider(host=host, port=port, username=username, password=password)

    # Default to MockEmailProvider for tests and safe local dev
    return MockEmailProvider()
