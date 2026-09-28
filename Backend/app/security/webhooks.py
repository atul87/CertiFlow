"""
Webhook security: HMAC-SHA256 signatures, timestamps, replay protection, and SSRF prevention (P8).
"""
from __future__ import annotations
import hmac
import hashlib
import secrets
import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple, Optional
from app.core.exceptions import ValidationError


class WebhookSecurity:
    @staticmethod
    def generate_secret() -> str:
        """Generate a cryptographically secure webhook secret."""
        return f"whsec_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_secret(secret: str) -> str:
        """Hash webhook secret for storage."""
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    @staticmethod
    def calculate_signature(secret: str, timestamp: int | str, payload: str | bytes) -> str:
        """
        Calculate HMAC-SHA256 signature over timestamp and raw payload:
        signature = HMAC-SHA256(secret, f"{timestamp}.{payload_str}")
        """
        payload_str = payload.decode("utf-8") if isinstance(payload, bytes) else str(payload)
        message = f"{timestamp}.{payload_str}".encode("utf-8")
        return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()

    generate_signature = calculate_signature

    @classmethod
    def verify_signature(
        cls,
        secret: str,
        signature: str,
        timestamp: int | str,
        payload: str | bytes,
        max_age_seconds: int = 300,
    ) -> bool:
        """
        Verify incoming webhook signature with constant-time comparison and timestamp tolerance.
        """
        import time
        now = int(time.time())
        ts_int = int(timestamp)
        if abs(now - ts_int) > max_age_seconds:
            return False  # Replay attack protection

        expected = cls.calculate_signature(secret, ts_int, payload)
        return hmac.compare_digest(expected, signature)


    @staticmethod
    def validate_destination_url(url: str) -> str:
        """
        Validate webhook destination URL and protect against Server-Side Request Forgery (SSRF).
        Disallows loopback, private networks, cloud metadata endpoints, and non-HTTP(S) schemes.
        """
        try:
            parsed = urlparse(url.strip())
        except Exception:
            raise ValidationError(message="Invalid webhook destination URL", code="INVALID_WEBHOOK_URL")

        if parsed.scheme not in ("http", "https"):
            raise ValidationError(
                message="Webhook URL must use http or https scheme",
                code="INVALID_WEBHOOK_SCHEME",
            )

        hostname = parsed.hostname
        if not hostname:
            raise ValidationError(message="Webhook URL must include a valid hostname", code="INVALID_WEBHOOK_URL")

        # Resolve IP and check for private / loopback / link-local addresses
        try:
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)

            # Deny private, loopback, link-local, multicast, reserved addresses
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip_str == "169.254.169.254"  # AWS/GCP metadata
            ):
                raise ValidationError(
                    message="Webhook destination URL cannot resolve to private, loopback, or metadata addresses (SSRF protection)",
                    code="WEBHOOK_SSRF_BLOCKED",
                )
        except socket.gaierror:
            # Domain could not be resolved
            raise ValidationError(
                message=f"Cannot resolve webhook host '{hostname}'",
                code="HOST_UNRESOLVABLE",
            )
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(message=f"Error validating webhook host: {str(e)}", code="INVALID_WEBHOOK_URL")

        return url.strip()
