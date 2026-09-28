from __future__ import annotations
import hmac
import hashlib
import time
import base64
import json
from typing import Optional
from app.core.config import settings


class SignedURLService:
    @classmethod
    def generate_token(cls, verification_code: str, expires_in_seconds: Optional[int] = None) -> str:
        """
        Generate an HMAC-SHA256 signed token for secure, temporary certificate download.
        """
        expiry_seconds = expires_in_seconds or (settings.SIGNED_URL_EXPIRY_HOURS * 3600)
        exp = int(time.time()) + expiry_seconds
        payload = {
            "code": verification_code.upper().strip(),
            "exp": exp,
        }
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode()
        payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode().rstrip("=")

        signature = hmac.new(
            settings.SIGNED_URL_SECRET.encode(),
            payload_b64.encode(),
            hashlib.sha256,
        ).hexdigest()

        return f"{payload_b64}.{signature}"

    @classmethod
    def verify_token(cls, verification_code: str, token: str) -> bool:
        """
        Validate token integrity and verify it has not expired.
        """
        if not token or "." not in token:
            return False
        try:
            payload_b64, signature = token.split(".", 1)

            # 1. Verify HMAC
            expected_sig = hmac.new(
                settings.SIGNED_URL_SECRET.encode(),
                payload_b64.encode(),
                hashlib.sha256,
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_sig):
                return False

            # 2. Decode payload & check expiry
            padding = "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_bytes.decode())

            if payload.get("code") != verification_code.upper().strip():
                return False

            if time.time() > payload.get("exp", 0):
                return False

            return True
        except Exception:
            return False

    @classmethod
    def build_download_url(cls, base_url: str, verification_code: str, expires_in_seconds: Optional[int] = None) -> str:
        token = cls.generate_token(verification_code, expires_in_seconds)
        clean_base = base_url.rstrip("/")
        return f"{clean_base}/api/v1/public/certificates/{verification_code.upper()}/download?token={token}"

    @classmethod
    def generate_signed_download_url(
        cls,
        certificate_id: str,
        organization_id: str,
        expires_in_hours: int = 24,
        base_url: str = "http://localhost:8000",
    ) -> str:
        return cls.build_download_url(
            base_url=base_url,
            verification_code=certificate_id,
            expires_in_seconds=expires_in_hours * 3600,
        )


SignedUrlService = SignedURLService
