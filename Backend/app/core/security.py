import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from app.core.config import settings

# Initialize Argon2id hasher
ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # 64 MB
    parallelism=1,
    hash_len=32,
    salt_len=16
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return ph.hash(password)


get_password_hash = hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def hash_token(raw_token: str) -> str:
    """Hash a token using SHA-256 for safe storage in the database."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_access_token(
    user_id: str,
    org_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "org_id": str(org_id) if org_id else None,
        "type": "access",
        "jti": secrets.token_hex(16),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def generate_refresh_token(
    user_id: str,
    org_id: Optional[str] = None
) -> Tuple[str, str, datetime]:
    """
    Generate an opaque high-entropy refresh token.
    Returns: (raw_token, token_hash, expires_at)
    The raw_token is returned to the user; token_hash is stored in MongoDB.
    """
    raw_token = secrets.token_urlsafe(48)
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return raw_token, token_hash, expires_at


def create_refresh_token(user_id: str, org_id: Optional[str] = None) -> str:
    """Helper returning only the raw refresh token string."""
    raw_token, _, _ = generate_refresh_token(user_id, org_id)
    return raw_token



def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises jwt.PyJWTError on invalid or expired token.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Token is not an access token")
    return payload


def generate_password_reset_token() -> Tuple[str, str, datetime]:
    """
    Generate a high-entropy, short-lived password reset token.
    Returns: (raw_token, token_hash, expires_at)
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    return raw_token, token_hash, expires_at
