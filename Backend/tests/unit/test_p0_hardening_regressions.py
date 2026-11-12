"""
Unit and regression tests for P0 Immediate Blockers & Hardening:
1. Asset loader pure sync without asyncio.run() / thread pool DB access
2. Elimination of web-server execution fallback when Redis is down (503 QUEUE_UNAVAILABLE)
3. Redis connection pool self-healing and reset after disconnect
4. Production secrets validator fails startup on default / insecure keys
5. Verification returns accurate issued_at datetime
6. Unique (organization_id, certificate_number) constraint and idempotency index
"""
from __future__ import annotations
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.config import Settings
from app.core.exceptions import AppException
from app.queue.redis import QueueManager
from app.services.certificate_service import _make_asset_loader, prefetch_template_assets
from app.services.verification_service import VerificationService
from app.schemas.issuance import IssuanceJobCreateRequest


# ---------------------------------------------------------------------------
# 1. Asset Loader Event-Loop & Pure-Sync Loader Test
# ---------------------------------------------------------------------------
@pytest.mark.no_db
def test_make_asset_loader_pure_sync_without_asyncio_run():
    """Verify _make_asset_loader returns a pure sync loader using in-memory preloaded cache."""
    test_asset_bytes = b"fake-png-signature-data"
    preloaded = {"asset_123": test_asset_bytes}
    loader = _make_asset_loader("org_abc", preloaded_assets=preloaded)

    # Calling loader synchronously must return cached bytes without invoking asyncio or DB
    result = loader("asset_123")
    assert result == test_asset_bytes

    # Missing asset must return None gracefully without raising RuntimeError or running loops
    missing = loader("asset_non_existent")
    assert missing is None


@pytest.mark.asyncio
async def test_prefetch_template_assets_extracts_and_loads():
    """Verify prefetch_template_assets collects all template asset IDs and queries repository once."""
    version_doc = {
        "background_asset_id": "bg_asset_1",
        "canvas": {
            "layers": [
                {"type": "image", "asset_id": "img_asset_2"},
                {"type": "signature", "signature_id": "sig_asset_3"},
                {"type": "text", "text": "Student Name"},
            ]
        }
    }

    mock_db_assets = {
        "bg_asset_1": {"id": "bg_asset_1", "storage_key": "storage/bg.png"},
        "img_asset_2": {"id": "img_asset_2", "storage_key": "storage/img.png"},
        "sig_asset_3": {"id": "sig_asset_3", "storage_key": "storage/sig.png"},
    }
    mock_file_bytes = {
        "storage/bg.png": b"bg_data",
        "storage/img.png": b"img_data",
        "storage/sig.png": b"sig_data",
    }

    with patch("app.repositories.asset_repository.AssetRepository.get_by_id", new_callable=AsyncMock) as mock_get_asset:
        mock_get_asset.side_effect = lambda aid: mock_db_assets.get(aid)
        with patch("app.services.storage_service.StorageService.read_file") as mock_read_file:
            mock_read_file.side_effect = lambda key: mock_file_bytes.get(key)
            loaded = await prefetch_template_assets(version_doc, "org_test")

            assert len(loaded) == 3
            assert loaded["bg_asset_1"] == b"bg_data"
            assert loaded["img_asset_2"] == b"img_data"
            assert loaded["sig_asset_3"] == b"sig_data"


# ---------------------------------------------------------------------------
# 2. Redis Queue Unavailable Raises 503 in Production (No Web Server Fallback)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_issuance_service_fails_with_503_when_queue_unavailable():
    """In production/staging, if Redis is down, fail fast with 503 QUEUE_UNAVAILABLE."""
    from app.services.issuance_service import IssuanceService

    tv_id = str(ObjectId())
    imp_id = str(ObjectId())
    req = IssuanceJobCreateRequest(
        import_id=imp_id,
        template_version_id=tv_id
    )

    with patch("app.repositories.template_version_repository.TemplateVersionRepository.get_by_id", new_callable=AsyncMock) as mock_tv:
        mock_tv.return_value = {"id": tv_id, "status": "published", "template_id": str(ObjectId())}
        with patch("app.repositories.import_repository.ImportRepository.get_by_id", new_callable=AsyncMock) as mock_imp:
            mock_imp.return_value = {"id": imp_id, "status": "validated"}
            with patch("app.repositories.issuance_job_repository.IssuanceJobRepository.count_active_jobs", new_callable=AsyncMock) as mock_count:
                mock_count.return_value = 0
                with patch("app.repositories.import_row_repository.ImportRowRepository.list_rows", new_callable=AsyncMock) as mock_rows:
                    mock_rows.return_value = ([{"id": str(ObjectId()), "row_number": 1, "data": {}}], 1)
                    with patch("app.queue.redis.QueueManager.enqueue", new_callable=AsyncMock) as mock_enqueue:
                        mock_enqueue.return_value = None  # Simulates queue down
                        with patch("app.core.config.settings.APP_ENV", "production"):
                            with pytest.raises(AppException) as exc_info:
                                await IssuanceService.create_job(
                                    request=req,
                                    org_id=str(ObjectId()),
                                    user_id=str(ObjectId()),
                                )
                            assert exc_info.value.status_code == 503
                            assert exc_info.value.code == "QUEUE_UNAVAILABLE"


# ---------------------------------------------------------------------------
# 3. Redis Pool Self-Healing and Reset
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_redis_pool_self_healing_reset():
    """Verify QueueManager detects disconnected pool, calls reset_pool, and reconnects."""
    await QueueManager.reset_pool()

    mock_pool = AsyncMock()
    # First ping raises ConnectionError (simulating Redis restart)
    mock_pool.ping.side_effect = ConnectionError("Connection lost")

    QueueManager._pool = mock_pool

    with patch("app.queue.redis.create_pool", new_callable=AsyncMock) as mock_create_pool:
        new_pool = AsyncMock()
        new_pool.ping.return_value = True
        mock_create_pool.return_value = new_pool

        # Calling get_pool should reset dead pool and establish new one
        pool = await QueueManager.get_pool()
        assert pool == new_pool
        assert QueueManager._pool == new_pool

    await QueueManager.reset_pool()


# ---------------------------------------------------------------------------
# 4. Production Secrets Validator Fails Startup on Default/Insecure Keys
# ---------------------------------------------------------------------------
@pytest.mark.no_db
def test_production_validator_rejects_insecure_defaults():
    """Startup must fail with ValueError if APP_ENV=production has default JWT secret."""
    with pytest.raises(ValueError, match="CRITICAL PRODUCTION SECURITY ERROR: Insecure or default JWT_SECRET_KEY"):
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="certiflow-local-dev-jwt-secret-key-must-be-long-and-secure-32chars",
            SIGNED_URL_SECRET="a-very-long-production-signed-url-secret-32ch",
            WEBHOOK_SIGNING_SECRET="a-very-long-production-webhook-secret-32ch",
            DEBUG=False
        )

    # Test short JWT secret rejection
    with pytest.raises(ValueError, match="at least 32 characters long"):
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="short-secret",
            SIGNED_URL_SECRET="a-very-long-production-signed-url-secret-32ch",
            WEBHOOK_SIGNING_SECRET="a-very-long-production-webhook-secret-32ch",
            DEBUG=False
        )

    # Test DEBUG=True rejection in production
    with pytest.raises(ValueError, match="DEBUG cannot be True in production"):
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="a-very-secure-random-jwt-secret-key-for-prod-9999",
            SIGNED_URL_SECRET="a-very-long-production-signed-url-secret-32ch",
            WEBHOOK_SIGNING_SECRET="a-very-long-production-webhook-secret-32ch",
            DEBUG=True
        )


@pytest.mark.no_db
def test_production_validator_passes_with_strong_secrets():
    """Settings must initialize cleanly in production when strong unique secrets are supplied."""
    from cryptography.fernet import Fernet
    prod_settings = Settings(
        APP_ENV="production",
        JWT_SECRET_KEY="a-very-secure-random-jwt-secret-key-for-prod-9999",
        ENCRYPTION_KEY=Fernet.generate_key().decode(),
        SIGNED_URL_SECRET="a-very-long-production-signed-url-secret-32ch",
        WEBHOOK_SIGNING_SECRET="a-very-long-production-webhook-secret-32ch",
        DEBUG=False
    )
    assert prod_settings.APP_ENV == "production"
    assert prod_settings.DEBUG is False


# ---------------------------------------------------------------------------
# 5. Verification Endpoint Populates issued_at Datetime
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_verification_service_returns_accurate_issued_at():
    """Verification must return the actual issued_at datetime, not None."""
    issued_time = datetime(2026, 9, 28, 10, 0, 0, tzinfo=timezone.utc)
    mock_cert = {
        "id": "cert_123",
        "organization_id": "org_123",
        "template_id": "tmpl_123",
        "template_version_id": "tv_123",
        "certificate_number": "CERT-2026-0001",
        "verification_code": "VCODE-12345",
        "status": "issued",
        "recipient": {"name": "Alice Wonderland", "email": "alice@example.com"},
        "data": {},
        "created_at": issued_time,
        "issued_at": issued_time,
        "metadata": {},
        "file": {}
    }

    with patch("app.services.rate_limiter.RateLimiter.is_allowed", new_callable=AsyncMock) as mock_rl:
        mock_rl.return_value = True
        with patch("app.services.verification_cache.VerificationCache.get", new_callable=AsyncMock) as mock_cache:
            mock_cache.return_value = None
            with patch("app.repositories.certificate_repository.CertificateRepository.get_by_verification_code", new_callable=AsyncMock) as mock_get_code:
                mock_get_code.return_value = mock_cert
                with patch("app.repositories.organization_repository.OrganizationRepository.get_by_id", new_callable=AsyncMock) as mock_org:
                    mock_org.return_value = {"id": "org_123", "name": "Acme Academy", "slug": "acme"}
                    with patch("app.repositories.template_repository.TemplateRepository.get_by_id", new_callable=AsyncMock) as mock_tmpl:
                        mock_tmpl.return_value = {"id": "tmpl_123", "name": "Data Science Master"}
                        with patch("app.repositories.verification_event_repository.VerificationEventRepository.create", new_callable=AsyncMock):
                            with patch("app.services.verification_cache.VerificationCache.set", new_callable=AsyncMock):
                                res = await VerificationService.verify_by_code("VCODE-12345")

                                assert res.status == "valid"
                                assert res.issued_at == issued_time
                                assert isinstance(res.issued_at, datetime)


# ---------------------------------------------------------------------------
# 6. Database Compound Unique Constraints
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_unique_org_certificate_number_constraint():
    """Database must enforce unique (organization_id, certificate_number)."""
    from app.core.database import DatabaseManager

    col = DatabaseManager.get_collection("certificates")
    org_id = ObjectId()
    cert_doc_1 = {
        "organization_id": org_id,
        "certificate_number": "CERT-UNIQUE-001",
        "verification_code": "VCODE-UNIQ-1",
        "status": "issued",
        "created_at": datetime.now(timezone.utc),
    }
    cert_doc_2 = {
        "organization_id": org_id,
        "certificate_number": "CERT-UNIQUE-001",  # Same number in same org
        "verification_code": "VCODE-UNIQ-2",
        "status": "issued",
        "created_at": datetime.now(timezone.utc),
    }

    await col.insert_one(cert_doc_1)
    with pytest.raises(DuplicateKeyError):
        await col.insert_one(cert_doc_2)


@pytest.mark.asyncio
async def test_idempotency_key_constraint_allows_nulls_but_blocks_duplicates():
    """Partial unique index on (organization_id, idempotency_key) must allow multiple nulls but block duplicate keys."""
    from app.core.database import DatabaseManager

    col = DatabaseManager.get_collection("certificates")
    org_id = ObjectId()

    # Multiple certificates with no idempotency key should succeed
    cert_no_key_1 = {
        "organization_id": org_id,
        "certificate_number": "CERT-NO-KEY-1",
        "verification_code": "VCODE-NK-1",
        "status": "issued",
        "created_at": datetime.now(timezone.utc),
    }
    cert_no_key_2 = {
        "organization_id": org_id,
        "certificate_number": "CERT-NO-KEY-2",
        "verification_code": "VCODE-NK-2",
        "status": "issued",
        "created_at": datetime.now(timezone.utc),
    }
    await col.insert_one(cert_no_key_1)
    await col.insert_one(cert_no_key_2)

    # First insertion with idempotency key succeeds
    cert_key_1 = {
        "organization_id": org_id,
        "certificate_number": "CERT-WITH-KEY-1",
        "verification_code": "VCODE-WK-1",
        "idempotency_key": "job_123_row_456",
        "status": "issued",
        "created_at": datetime.now(timezone.utc),
    }
    await col.insert_one(cert_key_1)

    # Second insertion with same idempotency key in same org must raise DuplicateKeyError
    cert_key_2 = {
        "organization_id": org_id,
        "certificate_number": "CERT-WITH-KEY-2",
        "verification_code": "VCODE-WK-2",
        "idempotency_key": "job_123_row_456",
        "status": "issued",
        "created_at": datetime.now(timezone.utc),
    }
    with pytest.raises(DuplicateKeyError):
        await col.insert_one(cert_key_2)
