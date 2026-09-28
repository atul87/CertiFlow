import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from app.services.recovery_service import RecoveryService
from app.core.database import DatabaseManager


@pytest.mark.asyncio
async def test_health_and_readiness_endpoints(client: AsyncClient):
    # 1. Root health
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # 2. Readiness probe
    ready_resp = await client.get("/health/ready")
    assert ready_resp.status_code == 200
    data = ready_resp.json()
    assert data["status"] == "ready"
    assert data["dependencies"]["mongodb"] == "ok"
    assert data["dependencies"]["storage"] == "ok"

    # 3. Version metadata
    ver_resp = await client.get("/api/v1/version")
    assert ver_resp.status_code == 200
    assert "version" in ver_resp.json()
    assert "commit" in ver_resp.json()

    # 4. Build metadata
    bld_resp = await client.get("/api/v1/build")
    assert bld_resp.status_code == 200
    assert bld_resp.json()["service"] == "certificate-api"

    # 5. Prometheus metrics exporter
    metrics_resp = await client.get("/metrics")
    assert metrics_resp.status_code == 200
    assert "text/plain" in metrics_resp.headers["content-type"]
    text = metrics_resp.text
    assert "certiflow_http_requests_total" in text


@pytest.mark.asyncio
async def test_security_headers_present_on_responses(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200

    # Production security headers
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in resp.headers.get("Permissions-Policy", "")
    assert "default-src 'self'" in resp.headers.get("Content-Security-Policy", "")


@pytest.mark.asyncio
async def test_worker_heartbeat_and_stuck_job_recovery():
    # 1. Record worker heartbeat
    worker_doc = await RecoveryService.record_worker_heartbeat(
        worker_id="test_worker_01",
        worker_type="certificate_worker",
        status="busy",
        current_job_id="job_stuck_123"
    )
    assert worker_doc["worker_id"] == "test_worker_01"

    worker_status = await RecoveryService.get_worker_status()
    assert worker_status["active_count"] >= 1

    # 2. Insert mock stuck issuance job
    db = DatabaseManager.get_db()
    old_time = datetime.now(timezone.utc) - timedelta(minutes=15)
    await db["issuance_jobs"].insert_one({
        "status": "processing",
        "retry_count": 0,
        "updated_at": old_time
    })

    # Insert a job that exceeded max retries (should transition to dead-letter / failed)
    await db["issuance_jobs"].insert_one({
        "status": "processing",
        "retry_count": 3,
        "updated_at": old_time
    })

    # 3. Trigger recovery service scan
    recovery_result = await RecoveryService.recover_stuck_jobs(timeout_seconds=300)
    assert recovery_result["recovered"] >= 1
    assert recovery_result["dead_letter"] >= 1
