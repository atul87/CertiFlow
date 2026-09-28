"""
CertificateIDService — P3.04 / P3.05 / P3.49 / P3.50

Generates:
  1. Sequential certificate number: CERT-<YEAR>-<NNNNNN>
  2. Cryptographically secure verification code (hex string)

Certificate number is built from an atomic MongoDB counter so concurrent
requests don't collide — no count() + 1 antipattern (P3.50).
"""
from __future__ import annotations
import secrets
import datetime
from app.repositories.certificate_repository import SequenceRepository


class CertificateIDService:

    @classmethod
    async def generate_certificate_number(
        cls,
        organization_id: str,
        prefix: str = "CERT",
        year: int | None = None,
    ) -> str:
        """
        Produce a zero-padded sequential certificate number:
            CERT-2026-000001
            CERT-2026-000002
            ...
        Thread-safe: MongoDB atomic $inc prevents duplicate numbers even under
        concurrent generation.
        """
        if year is None:
            year = datetime.datetime.now(datetime.timezone.utc).year

        counter = await SequenceRepository.next_val(
            organization_id=organization_id,
            key="certificate",
            year=year,
        )
        return f"{prefix}-{year}-{counter:06d}"

    @staticmethod
    def generate_verification_code(length: int = 16) -> str:
        """
        Generate a cryptographically secure, URL-safe hex verification code.
        Default 16 bytes → 32 hex chars.
        Never uses random.randint — uses secrets module (P3.05).
        """
        return secrets.token_hex(length).upper()

    @staticmethod
    def generate_verification_url(base_url: str, verification_code: str) -> str:
        """Build the full public verification URL embedded in the QR code."""
        base = base_url.rstrip("/")
        return f"{base}/verify/{verification_code}"
