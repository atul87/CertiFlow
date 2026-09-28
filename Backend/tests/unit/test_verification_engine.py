import pytest
import time
from datetime import datetime, timezone, timedelta
from app.services.rate_limiter import RateLimiter
from app.services.verification_cache import VerificationCache
from app.services.hash_service import HashService
from app.schemas.verification import (
    VerificationStatus,
    PublicVerificationResponse,
    PublicCertificateDetail,
    FileVerificationResponse,
    CertificateTimelineItem,
    IntegrityCheckResponse,
)

pytestmark = pytest.mark.no_db


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_under_limit(self):
        key = "test_user_allow"
        for _ in range(5):
            allowed = await RateLimiter.is_allowed(key, max_requests=10, window_seconds=60)
            assert allowed is True

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_over_limit(self):
        key = "test_user_block"
        for _ in range(3):
            assert await RateLimiter.is_allowed(key, max_requests=3, window_seconds=60) is True

        # 4th request within window must be blocked
        blocked = await RateLimiter.is_allowed(key, max_requests=3, window_seconds=60)
        assert blocked is False


class TestVerificationCache:
    @pytest.mark.asyncio
    async def test_cache_set_get_and_invalidate(self):
        code = "TESTCODE123"
        data = {
            "valid": True,
            "status": "valid",
            "certificate": {"certificate_number": "CERT-2026-0001", "recipient_name": "Atul Kumar"},
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

        # Set
        await VerificationCache.set(code, data, ttl=60)

        # Get
        cached = await VerificationCache.get(code)
        assert cached is not None
        assert cached["status"] == "valid"
        assert cached["certificate"]["recipient_name"] == "Atul Kumar"

        # Invalidate
        await VerificationCache.invalidate(code)
        cached_after = await VerificationCache.get(code)
        assert cached_after is None

    @pytest.mark.asyncio
    async def test_cache_invalidate_many(self):
        codes = ["CODE_A", "CODE_B"]
        await VerificationCache.set("CODE_A", {"status": "valid"}, ttl=60)
        await VerificationCache.set("CODE_B", {"status": "valid"}, ttl=60)

        assert await VerificationCache.get("CODE_A") is not None
        assert await VerificationCache.get("CODE_B") is not None

        await VerificationCache.invalidate_many(codes)

        assert await VerificationCache.get("CODE_A") is None
        assert await VerificationCache.get("CODE_B") is None


class TestTamperAndHashIntegrity:
    def test_sha256_deterministic(self):
        data = b"%PDF-1.4 original certificate content"
        hash1 = HashService.sha256(data)
        hash2 = HashService.sha256(data)
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_tamper_detection(self):
        original = b"%PDF-1.4 official certificate issued to Atul"
        altered = b"%PDF-1.4 official certificate issued to Hacker"

        hash_orig = HashService.sha256(original)
        hash_alt = HashService.sha256(altered)

        assert hash_orig != hash_alt


class TestVerificationSchemasAndPrivacy:
    def test_public_verification_response_contains_no_email(self):
        now = datetime.now(timezone.utc)
        resp = PublicVerificationResponse(
            valid=True,
            status="valid",
            certificate=PublicCertificateDetail(
                certificate_number="CERT-2026-0001",
                recipient_name="Atul Kumar",
                program_name="AI Workshop",
                issue_date="25 September 2026",
                issuer_name="ABC Institute",
            ),
            verified_at=now,
        )
        data_dict = resp.model_dump()
        assert "email" not in data_dict
        assert "recipient_email" not in data_dict
        assert "phone" not in data_dict
        assert "organization_id" not in data_dict
        assert "template_id" not in data_dict

    def test_revoked_response_structure(self):
        now = datetime.now(timezone.utc)
        resp = PublicVerificationResponse(
            valid=False,
            status="revoked",
            certificate=PublicCertificateDetail(
                certificate_number="CERT-2026-0001",
                recipient_name="Atul Kumar",
                public_download_available=False,
            ),
            revoked_at=now,
            revocation_reason="Incorrect recipient information",
            verified_at=now,
            message="This certificate was previously issued but has been revoked.",
        )
        assert resp.valid is False
        assert resp.status == "revoked"
        assert resp.revocation_reason == "Incorrect recipient information"
        assert resp.certificate.public_download_available is False

    def test_file_verification_response_structure(self):
        resp = FileVerificationResponse(
            valid=True,
            status="valid",
            integrity_matched=True,
            algorithm="SHA-256",
            file_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            certificate=PublicCertificateDetail(
                certificate_number="CERT-2026-0001",
                recipient_name="Atul Kumar",
            ),
            message="File matches authentic issued certificate.",
        )
        assert resp.valid is True
        assert resp.integrity_matched is True
        assert resp.algorithm == "SHA-256"

    def test_timeline_items_chronological_ordering(self):
        t0 = datetime(2026, 9, 25, 10, 0, tzinfo=timezone.utc)
        t1 = datetime(2026, 9, 26, 11, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 9, 28, 14, 0, tzinfo=timezone.utc)

        item1 = CertificateTimelineItem(type="generated", title="Issued", timestamp=t0)
        item2 = CertificateTimelineItem(type="verified_valid", title="Scan", timestamp=t1)
        item3 = CertificateTimelineItem(type="revoked", title="Revoked", timestamp=t2)

        # Unsorted list
        items = [item3, item1, item2]
        items.sort(key=lambda x: x.timestamp)

        assert items[0].type == "generated"
        assert items[1].type == "verified_valid"
        assert items[2].type == "revoked"
