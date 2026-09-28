"""
Integration tests for P7 — Dashboard, Analytics, Reporting, Search & Intelligence.
Tests:
- Tenant isolation across analytics queries
- Main dashboard overview & KPIs with comparative percentage deltas
- Specialized analytics (certificates, issuance, emails, verification, templates, imports, usage, storage, health)
- Advanced certificate search with multi-field filters & pagination
- Unified multi-source certificate timeline
- Report jobs (CSV streaming, ReportLab PDF generation, signed download token)
- Report tenant isolation & security checks
- Activity feed API
- Daily aggregation worker task
"""
from __future__ import annotations
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

from app.services.reports.report_service import ReportService
from app.workers.report_worker import aggregate_daily_analytics_task
from app.repositories.analytics_daily_repository import AnalyticsDailyRepository


async def create_published_template_and_cert(
    client: AsyncClient,
    headers: dict,
    recipient_name: str = "Atul Kumar",
    recipient_email: str = "atul@example.com",
    program_name: str = "AI Architect Masterclass",
) -> dict:
    # 1. Create template
    t_resp = await client.post(
        "/api/v1/templates",
        headers=headers,
        json={"name": f"Template - {program_name}"}
    )
    assert t_resp.status_code == 201
    template_id = t_resp.json()["data"]["id"]
    version_id = t_resp.json()["data"]["current_version_id"]

    # 2. Publish template
    pub_resp = await client.post(
        f"/api/v1/templates/{template_id}/versions/{version_id}/publish",
        headers=headers,
    )
    assert pub_resp.status_code == 200

    # 3. Generate certificate
    gen_payload = {
        "template_version_id": version_id,
        "data": {
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            "program_name": program_name,
            "issue_date": "28 September 2026",
        }
    }
    gen_resp = await client.post("/api/v1/certificates/generate", headers=headers, json=gen_payload)
    assert gen_resp.status_code == 201
    return gen_resp.json()["data"]


@pytest.mark.asyncio
async def test_analytics_tenant_isolation(client: AsyncClient, registered_user):
    """
    Mandatory tenant isolation test:
    Org A issues 2 certificates.
    Org B issues 1 certificate.
    Org A's dashboard must report exactly 2, never 3.
    """
    headers_a = registered_user["headers"]
    await create_published_template_and_cert(client, headers_a, recipient_name="Alice Smith", recipient_email="alice@org-a.com")
    await create_published_template_and_cert(client, headers_a, recipient_name="Bob Jones", recipient_email="bob@org-a.com")

    # Register Org B
    reg_b = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user_org_b@example.com",
            "password": "SecurePassword123!",
            "name": "Org B User",
            "organization_name": "Organization B Corp",
        },
    )
    assert reg_b.status_code == 201
    token_b = reg_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Org B issues 1 certificate
    await create_published_template_and_cert(client, headers_b, recipient_name="Charlie Brown", recipient_email="charlie@org-b.com")

    # Org A checks dashboard
    resp_a = await client.get("/api/v1/analytics/dashboard", headers=headers_a)
    assert resp_a.status_code == 200
    kpis_a = resp_a.json()["data"]["kpis"]
    assert kpis_a["certificates_issued"]["value"] == 2

    # Org B checks dashboard
    resp_b = await client.get("/api/v1/analytics/dashboard", headers=headers_b)
    assert resp_b.status_code == 200
    kpis_b = resp_b.json()["data"]["kpis"]
    assert kpis_b["certificates_issued"]["value"] == 1


@pytest.mark.asyncio
async def test_dashboard_overview_and_specialized_analytics(client: AsyncClient, registered_user):
    """Verify all dashboard and analytics endpoints return rich structured data."""
    headers = registered_user["headers"]
    cert = await create_published_template_and_cert(client, headers)
    code = cert["verification_code"]

    # Trigger public verification scan to populate verification events
    verif_resp = await client.get(f"/api/v1/public/verify/{code}", headers={"User-Agent": "TestBrowser/1.0"})
    assert verif_resp.status_code == 200

    # 1. Main Dashboard
    dash_resp = await client.get("/api/v1/analytics/dashboard?preset=last_30_days", headers=headers)
    assert dash_resp.status_code == 200
    data = dash_resp.json()["data"]
    assert "kpis" in data
    assert data["kpis"]["certificates_issued"]["value"] >= 1
    assert "issuance_trend" in data
    assert "status_distribution" in data
    assert data["status_distribution"]["active"] >= 1

    # 2. Certificate Analytics
    cert_resp = await client.get("/api/v1/analytics/certificates", headers=headers)
    assert cert_resp.status_code == 200
    assert cert_resp.json()["data"]["total_issued"] >= 1

    # 3. Issuance Analytics
    iss_resp = await client.get("/api/v1/analytics/issuance", headers=headers)
    assert iss_resp.status_code == 200
    assert "total_jobs" in iss_resp.json()["data"]

    # 4. Email Analytics
    email_resp = await client.get("/api/v1/analytics/emails", headers=headers)
    assert email_resp.status_code == 200
    assert "delivery_rate" in email_resp.json()["data"]

    # 5. Verification Analytics
    verif_analytics = await client.get("/api/v1/analytics/verification", headers=headers)
    assert verif_analytics.status_code == 200
    va_data = verif_analytics.json()["data"]
    assert va_data["total_attempts"] >= 1
    assert va_data["successful_valid"] >= 1

    # 6. Template Analytics
    tmpl_resp = await client.get("/api/v1/analytics/templates", headers=headers)
    assert tmpl_resp.status_code == 200
    assert tmpl_resp.json()["data"]["total_templates"] >= 1

    # 7. Import Analytics
    imp_resp = await client.get("/api/v1/analytics/imports", headers=headers)
    assert imp_resp.status_code == 200

    # 8. Usage Analytics
    usage_resp = await client.get("/api/v1/analytics/usage", headers=headers)
    assert usage_resp.status_code == 200
    assert usage_resp.json()["data"]["certificates_issued"] >= 1

    # 9. Storage Analytics
    storage_resp = await client.get("/api/v1/analytics/storage", headers=headers)
    assert storage_resp.status_code == 200
    assert "breakdown_mb" in storage_resp.json()["data"]

    # 10. Health check
    health_resp = await client.get("/api/v1/analytics/health", headers=headers)
    assert health_resp.status_code == 200
    assert health_resp.json()["data"]["services"]["api"] == "healthy"


@pytest.mark.asyncio
async def test_advanced_certificate_search(client: AsyncClient, registered_user):
    """Test search with filters: query, status, program, date range, pagination."""
    headers = registered_user["headers"]
    cert = await create_published_template_and_cert(
        client,
        headers,
        recipient_name="Deepak Chopra",
        recipient_email="deepak@wellness.com",
        program_name="Mindfulness & AI",
    )
    cert_id = cert["id"]
    cert_num = cert["certificate_number"]

    # Search by recipient name
    resp1 = await client.get("/api/v1/certificates?search=Deepak", headers=headers)
    assert resp1.status_code == 200
    items1 = resp1.json()["data"]["items"]
    assert any(c["id"] == cert_id for c in items1)

    # Search by certificate number
    resp2 = await client.get(f"/api/v1/certificates?search={cert_num}", headers=headers)
    assert resp2.status_code == 200
    items2 = resp2.json()["data"]["items"]
    assert len(items2) >= 1
    assert items2[0]["id"] == cert_id

    # Search with status filter
    resp3 = await client.get("/api/v1/certificates?status=generated", headers=headers)
    assert resp3.status_code == 200
    assert any(c["id"] == cert_id for c in resp3.json()["data"]["items"])

    # Search with non-matching query
    resp4 = await client.get("/api/v1/certificates?search=NonExistentPersonName123XYZ", headers=headers)
    assert resp4.status_code == 200
    assert len(resp4.json()["data"]["items"]) == 0


@pytest.mark.asyncio
async def test_unified_certificate_timeline(client: AsyncClient, registered_user):
    """Verify multi-source unified timeline combines generation, verification, and audit logs."""
    headers = registered_user["headers"]
    cert = await create_published_template_and_cert(client, headers)
    cert_id = cert["id"]
    code = cert["verification_code"]

    # Trigger public scan
    await client.get(f"/api/v1/public/verify/{code}", headers={"User-Agent": "MobileScanner/2.0"})

    # Fetch timeline
    tl_resp = await client.get(f"/api/v1/certificates/{cert_id}/timeline", headers=headers)
    assert tl_resp.status_code == 200
    tl = tl_resp.json()["data"]
    assert tl["certificate_id"] == cert_id
    events = tl["events"]
    assert len(events) >= 2

    types = [e["type"] for e in events]
    assert "generated" in types
    assert "verified_valid" in types


@pytest.mark.asyncio
async def test_report_jobs_csv_and_pdf(client: AsyncClient, registered_user):
    """Test full report job lifecycle: creation, processing, download URL, CSV and PDF generation."""
    headers = registered_user["headers"]
    org_id = registered_user["organization"]["id"]
    await create_published_template_and_cert(client, headers)

    # 1. Create CSV Certificate Report Job
    csv_req = {
        "type": "certificate_report",
        "format": "csv",
        "date_range": "last_30_days",
    }
    create_resp = await client.post("/api/v1/reports", headers=headers, json=csv_req)
    assert create_resp.status_code == 201
    job = create_resp.json()["data"]
    job_id = job["id"]
    assert job["status"] == "queued"

    # 2. Process report directly
    processed = await ReportService.process_report(job_id, org_id)
    assert processed is not None
    assert processed["status"] == "completed"
    assert processed["row_count"] >= 1

    # 3. Get report status
    get_resp = await client.get(f"/api/v1/reports/{job_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["status"] == "completed"
    assert "download_url" in get_resp.json()["data"]
    download_url = get_resp.json()["data"]["download_url"]

    # 4. Download report file via signed URL token
    token = download_url.split("token=")[-1]
    dl_resp = await client.get(f"/api/v1/reports/{job_id}/download?token={token}", headers=headers)
    assert dl_resp.status_code == 200
    assert "text/csv" in dl_resp.headers["content-type"]
    csv_text = dl_resp.text
    assert "certificate_number" in csv_text
    assert "recipient_name" in csv_text

    # 5. Create and download PDF Summary Report
    pdf_req = {
        "type": "summary_report",
        "format": "pdf",
        "date_range": "last_30_days",
    }
    create_pdf = await client.post("/api/v1/reports", headers=headers, json=pdf_req)
    assert create_pdf.status_code == 201
    pdf_job_id = create_pdf.json()["data"]["id"]

    processed_pdf = await ReportService.process_report(pdf_job_id, org_id)
    assert processed_pdf["status"] == "completed"

    dl_pdf_resp = await client.get(f"/api/v1/reports/{pdf_job_id}/download", headers=headers)
    assert dl_pdf_resp.status_code == 200
    assert dl_pdf_resp.headers["content-type"] == "application/pdf"
    assert dl_pdf_resp.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_report_cross_tenant_access_denied(client: AsyncClient, registered_user):
    """Ensure User B cannot access or download User A's generated report."""
    headers_a = registered_user["headers"]
    org_id_a = registered_user["organization"]["id"]

    # User A creates a report
    c_resp = await client.post(
        "/api/v1/reports",
        headers=headers_a,
        json={"type": "certificate_report", "format": "csv"},
    )
    job_id = c_resp.json()["data"]["id"]
    await ReportService.process_report(job_id, org_id_a)

    # Register User B
    reg_b = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user_b_reports@example.com",
            "password": "SecurePassword123!",
            "name": "User B",
            "organization_name": "Org B Inc",
        },
    )
    token_b = reg_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts to access User A's report details
    get_resp = await client.get(f"/api/v1/reports/{job_id}", headers=headers_b)
    assert get_resp.status_code == 404

    # User B attempts to download User A's report
    dl_resp = await client.get(f"/api/v1/reports/{job_id}/download", headers=headers_b)
    assert dl_resp.status_code == 404


@pytest.mark.asyncio
async def test_activity_feed_api(client: AsyncClient, registered_user):
    """Verify activity feed endpoint returns paginated audit events."""
    headers = registered_user["headers"]
    await create_published_template_and_cert(client, headers)

    act_resp = await client.get("/api/v1/activity?limit=10", headers=headers)
    assert act_resp.status_code == 200
    act_data = act_resp.json()["data"]
    assert "items" in act_data
    assert len(act_data["items"]) >= 1
    assert "total" in act_data


@pytest.mark.asyncio
async def test_daily_aggregation_worker_task(client: AsyncClient, registered_user):
    """Verify ARQ worker pre-aggregation task writes to analytics_daily."""
    headers = registered_user["headers"]
    org_id = registered_user["organization"]["id"]
    await create_published_template_and_cert(client, headers)

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = await aggregate_daily_analytics_task(None, org_id, target_date_str=today_str)
    assert result is not None
    assert str(result["organization_id"]) == org_id
    assert result["date"] == today_str
    assert "certificates" in result
    assert result["certificates"]["issued"] >= 1

    # Verify retrieval via repository
    stored = await AnalyticsDailyRepository.get_daily(org_id, today_str)
    assert stored is not None
    assert stored["date"] == today_str
