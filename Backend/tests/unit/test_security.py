import pytest
from datetime import timedelta
import jwt
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_token
)


def test_password_hashing():
    password = "SuperSecretPassword123"
    hashed = hash_password(password)

    # Password hash must not equal plaintext
    assert hashed != password
    assert hashed.startswith("$argon2id$")

    # Correct password verifies
    assert verify_password(password, hashed) is True

    # Incorrect password fails
    assert verify_password("WrongPassword123", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_access_token():
    user_id = "60c72b2f9b1d8b2bad000001"
    org_id = "60c72b2f9b1d8b2bad000002"

    token = create_access_token(user_id=user_id, org_id=org_id)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["org_id"] == org_id
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_expired_jwt_token():
    user_id = "60c72b2f9b1d8b2bad000001"
    # Create token expired 1 second ago
    token = create_access_token(user_id=user_id, expires_delta=timedelta(seconds=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_invalid_jwt_token():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("completely-invalid-jwt-token")


def test_refresh_token_generation_and_hashing():
    raw_token, token_hash, expires_at = generate_refresh_token(
        user_id="user_123",
        org_id="org_456"
    )

    assert len(raw_token) > 30
    assert len(token_hash) == 64  # SHA-256 hex string length
    assert hash_token(raw_token) == token_hash
    assert hash_token("different_token") != token_hash
