"""
Unit and regression tests for P3 — Production Infrastructure & Reliability:
Item 20 & 21: StorageProvider abstraction (LocalStorageProvider & S3StorageProvider)
Item 22 & 23: Outbox event pattern, exponential backoff, and dead-letter handling
Item 24: Worker & queue operational metrics
Item 25: Structured logging with contextvars
"""
from __future__ import annotations
import pytest
import logging
from unittest.mock import AsyncMock, patch
from bson import ObjectId

from app.services.storage.providers import LocalStorageProvider, S3StorageProvider
from app.repositories.outbox_repository import OutboxRepository
from app.workers.outbox_worker import process_outbox_events_task
from app.services.queue_metrics_service import QueueMetricsService
from app.core.logging import set_log_context, StructuredLogFilter


# ---------------------------------------------------------------------------
# 1. Item 20 & 21: Storage Provider Abstraction
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_local_storage_provider_crud(tmp_path):
    """Verify LocalStorageProvider writes, reads, exists, and deletes files."""
    provider = LocalStorageProvider(base_dir=str(tmp_path))
    test_key = "assets/org1/cert.png"
    content = b"sample-png-bytes"

    # Save
    saved_key = await provider.save_file(test_key, content, content_type="image/png")
    assert saved_key == test_key

    # Exists & Read
    assert await provider.exists(test_key) is True
    read_bytes = await provider.read_file(test_key)
    assert read_bytes == content

    # Delete
    deleted = await provider.delete_file(test_key)
    assert deleted is True
    assert await provider.exists(test_key) is False


@pytest.mark.asyncio
async def test_s3_storage_provider_crud():
    """Verify S3StorageProvider interface and mock store operation."""
    provider = S3StorageProvider(bucket_name="my-bucket", region="eu-west-1")
    test_key = "certificates/2026/cert-001.pdf"
    content = b"%PDF-1.4 sample data"

    # Save
    saved_key = await provider.save_file(test_key, content, content_type="application/pdf")
    assert saved_key == test_key

    # Exists & Read
    assert await provider.exists(test_key) is True
    read_bytes = await provider.read_file(test_key)
    assert read_bytes == content

    # Public URL
    url = provider.get_public_url(test_key)
    assert "my-bucket" in url
    assert test_key in url

    # Delete
    assert await provider.delete_file(test_key) is True
    assert await provider.exists(test_key) is False


# ---------------------------------------------------------------------------
# 2. Item 22 & 23: Outbox Pattern, Exponential Backoff & Dead-Letter Queue
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_outbox_lifecycle_backoff_and_dead_letter():
    """Verify outbox event creation, retry with backoff, and transition to dead_letter."""
    org_id = str(ObjectId())

    # 1. Create outbox event with max_attempts=2
    event = await OutboxRepository.create_event(
        org_id=org_id,
        event_type="certificate.issued",
        destination_type="webhook",
        payload={"certificate_id": "c1", "delivery_id": "d1"},
        max_attempts=2,
    )
    event_id = event["event_id"]
    assert event["status"] == "pending"

    # 2. First failure -> should transition to retrying
    status_1 = await OutboxRepository.record_failure(
        event_id=event_id,
        error_message="Network connection refused",
        backoff_seconds=5,
    )
    assert status_1 == "retrying"

    # 3. Second failure (reaching max_attempts=2) -> should transition to dead_letter
    status_2 = await OutboxRepository.record_failure(
        event_id=event_id,
        error_message="Host unreachable",
        backoff_seconds=10,
    )
    assert status_2 == "dead_letter"

    # Verify dead letter appears in list_dead_letters
    dead_letters = await OutboxRepository.list_dead_letters(org_id=org_id)
    assert len(dead_letters) >= 1
    assert dead_letters[0]["event_id"] == event_id
    assert dead_letters[0]["status"] == "dead_letter"


@pytest.mark.asyncio
async def test_outbox_worker_processes_and_delivers_successfully():
    """Verify outbox worker delivers events and marks them delivered."""
    org_id = str(ObjectId())
    event = await OutboxRepository.create_event(
        org_id=org_id,
        event_type="certificate.issued",
        destination_type="webhook",
        payload={"delivery_id": "deliv_123"},
    )
    event_id = event["event_id"]

    with patch("app.workers.webhook_worker.deliver_webhook_task", new_callable=AsyncMock) as mock_deliver:
        res = await process_outbox_events_task(batch_size=10)
        assert res["status"] == "ok"
        assert res["delivered"] >= 1


# ---------------------------------------------------------------------------
# 3. Item 24: Queue & Worker Metrics
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_queue_metrics_service_reports_depth_and_health():
    """Verify QueueMetricsService aggregates pending counts and Redis status."""
    metrics = await QueueMetricsService.get_metrics()

    assert "jobs" in metrics
    assert "items" in metrics
    assert "outbox" in metrics
    assert "queue_depth_pending" in metrics["items"]
    assert "pending_events" in metrics["outbox"]
    assert "dead_letter_events" in metrics["outbox"]


# ---------------------------------------------------------------------------
# 4. Item 25: Structured Logging Context
# ---------------------------------------------------------------------------
@pytest.mark.no_db
def test_structured_logging_context_filter():
    """Verify StructuredLogFilter injects context variables into log records."""
    set_log_context(
        request_id="req_test_123",
        job_id="job_test_456",
        organization_id="org_test_789",
        certificate_id="cert_test_999",
    )

    filter_obj = StructuredLogFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    filter_obj.filter(record)
    assert record.request_id == "req_test_123"
    assert record.job_id == "job_test_456"
    assert record.organization_id == "org_test_789"
    assert record.certificate_id == "cert_test_999"
