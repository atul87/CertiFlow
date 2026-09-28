"""
API Key generation, hashing, and validation utilities (P8).
Keys follow format: ck_live_<32-chars-urlsafe-secret>
Stored securely as SHA-256 hash. The plaintext secret is never persisted.
"""
from __future__ import annotations
import secrets
import hashlib
from typing import Tuple
from app.core.config import settings


class APIKeySecurity:
    @classmethod
    def generate_api_key(cls, is_test: bool = False) -> Tuple[str, str, str]:
        """
        Generate a new high-entropy API key.
        Returns:
            raw_key: Full plaintext key (shown once to user, e.g. ck_live_...)
            key_hash: SHA-256 hash of the full key for database storage
            prefix: Short identifiable prefix for listing (e.g. ck_live_a1b2)
        """
        prefix = settings.API_KEY_PREFIX_TEST if is_test else settings.API_KEY_PREFIX_LIVE
        random_part = secrets.token_urlsafe(32)
        raw_key = f"{prefix}{random_part}"
        key_hash = cls.hash_key(raw_key)
        display_prefix = raw_key[:12]
        return raw_key, key_hash, display_prefix

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Calculate SHA-256 hash of an API key or invitation token."""
        return hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()
