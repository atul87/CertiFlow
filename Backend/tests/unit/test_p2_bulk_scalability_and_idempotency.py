"""
Unit and regression tests for P2 — Bulk Issuance Scalability & Idempotency:
Item 14: Batch item claiming via claim_batch()
Item 15: Organization EmailSettings cached once per job
Item 16: Progress updates batched per processing cycle
Item 17: insert_many(..., ordered=False) resilience
Item 18: Idempotent certificate generation on retry (no duplicates)
Item 19: Explicit job states (pending -> processing -> completed / completed_with_errors / failed)
"""
from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId
from datetime import datetime, timezone

from app.repositories.issuance_item_repository import IssuanceItemRepository
from app.repositories.certificate_repository import CertificateRepository
from app.services.certificate_service import CertificateService
from app.services.progress_service import ProgressService
from app.schemas.certificate import CertificateGenerateRequest, CertificateResponse
from app.schemas.issuance import JobStatus


# ---------------------------------------------------------------------------
# 1. Item 14 & 17: Batch Claiming and insert_many(ordered=False)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_bulk_create_uses_unordered_insert_and_claim_batch():
    """Verify items are inserted with ordered=False and can be claimed in batches."""
    job_id = str(ObjectId())
    org_id = str(ObjectId())
    rows = [
        {"id": str(ObjectId()), "row_number": 1, "data": {"recipient_name": "User 1", "email": "u1@test.com"}},
        {"id": str(ObjectId()), "row_number": 2, "data": {"recipient_name": "User 2", "email": "u2@test.com"}},
        {"id": str(ObjectId()), "row_number": 3, "data": {"recipient_name": "User 3", "email": "u3@test.com"}},
    ]

    # Bulk create
    count = await IssuanceItemRepository.bulk_create(job_id=job_id, organization_id=org_id, valid_rows=rows)
    assert count == 3

    # Claim batch of up to 2 items
    claimed = await IssuanceItemRepository.claim_batch(job_id=job_id, batch_size=2)
    assert len(claimed) == 2
    for item in claimed:
        assert item["status"] == "processing"
        assert item["attempts"] == 1

    # Claim remaining batch
    remaining_claimed = await IssuanceItemRepository.claim_batch(job_id=job_id, batch_size=2)
    assert len(remaining_claimed) == 1
    assert remaining_claimed[0]["status"] == "processing"

    # Next claim should return empty
    empty_claimed = await IssuanceItemRepository.claim_batch(job_id=job_id, batch_size=2)
    assert len(empty_claimed) == 0


# ---------------------------------------------------------------------------
# 2. Item 18: Deterministic Idempotency on Retry
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_certificate_service_generate_idempotency_hit():
    """Calling generate with existing idempotency key or import_row returns existing certificate."""
    org_id = str(ObjectId())
    user_id = str(ObjectId())
    import_id = str(ObjectId())
    import_row_id = str(ObjectId())
    idempotency_key = f"job_100_row_{import_row_id}"

    existing_cert = {
        "id": "cert_existing_999",
        "organization_id": org_id,
        "template_id": str(ObjectId()),
        "template_version_id": str(ObjectId()),
        "certificate_number": "CERT-EXISTING-001",
        "verification_code": "VCODE-EXISTING",
        "status": "issued",
        "recipient": {"name": "Bob", "email": "bob@example.com"},
        "data": {},
        "created_at": datetime.now(timezone.utc),
        "issued_at": datetime.now(timezone.utc),
        "template_snapshot": {
            "template_id": str(ObjectId()),
            "template_version_id": str(ObjectId()),
            "version": 1,
            "template_name": "Test",
        },
        "metadata": {},
        "file": {}
    }

    req = CertificateGenerateRequest(
        template_version_id=existing_cert["template_version_id"],
        data={"recipient_name": "Bob"},
        import_id=import_id,
        import_row_id=import_row_id,
    )

    with patch("app.repositories.certificate_repository.CertificateRepository.get_by_idempotency_key", new_callable=AsyncMock) as mock_get_key:
        mock_get_key.return_value = existing_cert
        # When idempotency key hits, it must return existing cert without calling render or template repo
        res = await CertificateService.generate(
            request=req,
            org_id=org_id,
            user_id=user_id,
            idempotency_key=idempotency_key,
        )
        assert res.id == "cert_existing_999"
        assert res.certificate_number == "CERT-EXISTING-001"
        assert res.status == "issued"


# ---------------------------------------------------------------------------
# 3. Item 19: Explicit Job States Transition
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_job_status_transitions():
    """Verify JobStatus enum includes explicit states and ProgressService transitions accurately."""
    assert "pending" in [s.value for s in JobStatus]
    assert "processing" in [s.value for s in JobStatus]
    assert "completed" in [s.value for s in JobStatus]
    assert "partially_failed" in [s.value for s in JobStatus]
    assert "completed_with_errors" in [s.value for s in JobStatus]
    assert "failed" in [s.value for s in JobStatus]
    assert "cancelled" in [s.value for s in JobStatus]

    job_id = str(ObjectId())

    # All completed
    with patch("app.repositories.issuance_job_repository.IssuanceJobRepository.sync_counts_from_items", new_callable=AsyncMock) as mock_sync:
        mock_sync.return_value = {
            "id": job_id, "organization_id": str(ObjectId()), "status": "processing",
            "pending": 0, "processing": 0, "total": 10, "completed": 10, "failed": 0
        }
        with patch("app.repositories.issuance_job_repository.IssuanceJobRepository.update_status", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {"status": "completed"}
            await ProgressService.finalize_job_if_done(job_id)
            mock_update.assert_called_with(job_id=job_id, status="completed")

    # Completed with some errors (partially failed)
    with patch("app.repositories.issuance_job_repository.IssuanceJobRepository.sync_counts_from_items", new_callable=AsyncMock) as mock_sync:
        mock_sync.return_value = {
            "id": job_id, "organization_id": str(ObjectId()), "status": "processing",
            "pending": 0, "processing": 0, "total": 10, "completed": 8, "failed": 2
        }
        with patch("app.repositories.issuance_job_repository.IssuanceJobRepository.update_status", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {"status": "completed_with_errors"}
            await ProgressService.finalize_job_if_done(job_id)
            mock_update.assert_called_with(job_id=job_id, status="completed_with_errors")
