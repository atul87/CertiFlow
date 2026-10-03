import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_production_rejects_default_jwt_secret():
    """Verify that Settings fails startup in production when default JWT secret is used."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            DEBUG=False,
            ALLOW_DEMO_AUTH=False,
            JWT_SECRET_KEY="certiflow-local-dev-jwt-secret-key-must-be-long-and-secure-32chars",
            SIGNED_URL_SECRET="secure-random-signed-url-secret-32ch",
            WEBHOOK_SIGNING_SECRET="secure-random-webhook-secret-32ch",
        )
    assert "Insecure or default JWT_SECRET_KEY" in str(exc_info.value)


def test_production_rejects_short_jwt_secret():
    """Verify that Settings fails startup in production when JWT secret is under 32 chars."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            DEBUG=False,
            ALLOW_DEMO_AUTH=False,
            JWT_SECRET_KEY="short-secret",
            SIGNED_URL_SECRET="secure-random-signed-url-secret-32ch",
            WEBHOOK_SIGNING_SECRET="secure-random-webhook-secret-32ch",
        )
    assert "at least 32 characters long" in str(exc_info.value)


def test_production_rejects_debug_mode():
    """Verify that Settings fails startup in production when DEBUG=True."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            DEBUG=True,
            ALLOW_DEMO_AUTH=False,
            JWT_SECRET_KEY="a" * 40,
            SIGNED_URL_SECRET="b" * 32,
            WEBHOOK_SIGNING_SECRET="c" * 32,
        )
    assert "DEBUG cannot be True in production" in str(exc_info.value)


def test_production_rejects_demo_auth():
    """Verify that Settings fails startup in production when ALLOW_DEMO_AUTH=True."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            DEBUG=False,
            ALLOW_DEMO_AUTH=True,
            JWT_SECRET_KEY="a" * 40,
            SIGNED_URL_SECRET="b" * 32,
            WEBHOOK_SIGNING_SECRET="c" * 32,
        )
    assert "ALLOW_DEMO_AUTH must be False in production" in str(exc_info.value)


def test_production_accepts_valid_hardened_config():
    """Verify that Settings loads cleanly when production secrets are hardened and valid."""
    s = Settings(
        APP_ENV="production",
        DEBUG=False,
        ALLOW_DEMO_AUTH=False,
        JWT_SECRET_KEY="x" * 64,
        SIGNED_URL_SECRET="y" * 32,
        WEBHOOK_SIGNING_SECRET="z" * 32,
    )
    assert s.APP_ENV == "production"
    assert s.DEBUG is False
    assert s.ALLOW_DEMO_AUTH is False
