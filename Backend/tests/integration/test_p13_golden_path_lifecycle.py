import io
import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.issuance_job_repository import IssuanceJobRepository
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.services.issuance_service import IssuanceService


@pytest.mark.asyncio
async def test_p13_golden_path_certificate_issuance_lifecycle(client: AsyncClient):
    """
    P13 Golden-Path Integration Test:
    CSV upload
       ↓
    column mapping & validation
       ↓
    batch job creation
       ↓
    queue & worker execution
       ↓
    template rendering & smart fit
       ↓
    PDF generation & SHA-256 hashing
       ↓
    verifiable credential generation
       ↓
    database persistence
       ↓
    outbox email dispatch
       ↓
    verification URL & public verification check
       ↓
    public PDF download verification
    """
    client.cookies.clear()

    # 1. Organization & User Registration via hardened session auth (P13.1)
    reg_payload = {
        "name": "Dean Minerva McGonagall",
        "email": "mcgonagall@goldenpath.edu",
        "password": "Transfiguration#2026!",
        "organization_name": "Golden Path Academy of Excellence"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    auth_data = reg_res.json()["data"]
    access_token = auth_data["access_token"]
    org_id = auth_data["organization"]["id"]
    csrf_token = client.cookies.get(settings.COOKIE_CSRF_NAME)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-CSRF-Token": csrf_token or ""
    }

    # 2. Design and publish Certificate Template
    tmpl_res = await client.post(
        "/api/v1/templates",
        headers=headers,
        json={
            "name": "Advanced Full Stack Honors Certificate",
            "description": "Golden path production certification template",
            "canvas": {"width": 842, "height": 595, "unit": "px", "dpi": 72}
        }
    )
    assert tmpl_res.status_code == 201
    template_id = tmpl_res.json()["data"]["id"]
    version_id = tmpl_res.json()["data"]["current_version_id"]

    # Add text and QR elements to version
    update_res = await client.put(
        f"/api/v1/templates/{template_id}/versions/{version_id}",
        headers=headers,
        json={
            "elements": [
                {
                    "id": "elem_recip_name",
                    "type": "text",
                    "x": 100,
                    "y": 200,
                    "width": 600,
                    "height": 50,
                    "content": "{{recipient_name}}",
                    "fontSize": 32,
                    "fontWeight": "bold",
                    "color": "#111827",
                    "textAlign": "center"
                },
                {
                    "id": "elem_course_name",
                    "type": "text",
                    "x": 100,
                    "y": 280,
                    "width": 600,
                    "height": 40,
                    "content": "For successfully completing {{course_name}}",
                    "fontSize": 20,
                    "fontWeight": "normal",
                    "color": "#374151",
                    "textAlign": "center"
                },
                {
                    "id": "elem_qr_code",
                    "type": "qr",
                    "x": 680,
                    "y": 440,
                    "width": 100,
                    "height": 100,
                    "content": "https://verify.certiflow.io/verify/{{verification_code}}"
                }
            ]
        }
    )
    assert update_res.status_code == 200

    # Publish template version
    pub_res = await client.post(f"/api/v1/templates/{template_id}/versions/{version_id}/publish", headers=headers)
    assert pub_res.status_code == 200

    # 3. CSV Upload (Multi-recipient dataset)
    csv_content = (
        "Full Name,Email Address,Course Name,Completion Date\n"
        "Sarah Connor,sarah.connor@cyberdyne.org,Cyber Security & Defense,30 September 2026\n"
        "Kyle Reese,kyle.reese@resistance.mil,Tactical Networking & AI,30 September 2026\n"
    ).encode("utf-8")

    files = {"file": ("students_q3.csv", io.BytesIO(csv_content), "text/csv")}
    form_data = {"template_id": template_id, "template_version_id": version_id}
    upload_res = await client.post(
        "/api/v1/imports",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
        data=form_data
    )
    assert upload_res.status_code == 201
    import_id = upload_res.json()["data"]["id"]

    # 4. Map columns to system placeholders and trigger validation
    mapping_payload = {
        "mappings": [
            {"source_column": "Full Name", "target_field": "recipient_name"},
            {"source_column": "Email Address", "target_field": "recipient_email"},
            {"source_column": "Course Name", "target_field": "course_name"},
            {"source_column": "Completion Date", "target_field": "issue_date"},
        ]
    }
    map_res = await client.post(f"/api/v1/imports/{import_id}/mapping", headers=headers, json=mapping_payload)
    assert map_res.status_code == 200
    assert map_res.json()["data"]["valid_rows"] == 2

    # 5. Create Issuance Job targeting the validated import and published template
    job_payload = {
        "template_version_id": version_id,
        "import_id": import_id,
    }
    job_res = await client.post("/api/v1/issuance-jobs", headers=headers, json=job_payload)
    assert job_res.status_code == 201
    job_data = job_res.json()["data"]
    job_id = job_data["id"]
    assert job_data["total"] == 2

    # 6. Execute issuance worker engine (Stateless, crash-safe ARQ worker)
    from app.workers.certificate_worker import generate_bulk_certificates_task
    worker_res = await generate_bulk_certificates_task(None, job_id, org_id)
    assert worker_res["status"] == "ok"
    assert worker_res["processed_items"] == 2

    # Verify job status in repository
    completed_job = await IssuanceJobRepository.get_by_id(job_id)
    assert completed_job is not None
    assert completed_job["status"] == "completed"
    assert completed_job["completed"] == 2

    # 7. Database persistence verification
    certs, total = await CertificateRepository.list_certificates(org_id)
    assert total >= 2
    assert len(certs) >= 2

    sarah_cert = next(c for c in certs if c.get("recipient", {}).get("name") == "Sarah Connor" or c.get("data", {}).get("recipient_name") == "Sarah Connor")
    assert sarah_cert["certificate_number"].startswith("CERT-")
    assert sarah_cert["status"] in ("generated", "active")
    assert sarah_cert.get("file", {}).get("pdf_key") is not None
    assert len(sarah_cert.get("file", {}).get("sha256", "")) == 64  # SHA-256 hex length

    verification_code = sarah_cert["verification_code"]
    cert_id = sarah_cert["id"]

    # 8. Dispatch Email Delivery Job for generated certificates
    cert_ids = [c["id"] for c in certs]
    email_job_res = await client.post(
        "/api/v1/email-jobs",
        headers=headers,
        json={"certificate_ids": cert_ids, "delivery_mode": "link"}
    )
    assert email_job_res.status_code == 201

    # Verify Email dispatch outbox records were created for recipients
    deliveries, d_total = await EmailDeliveryRepository.list_deliveries(organization_id=org_id)
    assert d_total >= 2
    assert len(deliveries) >= 2

    # 9. Public Verification Check (Privacy-preserving public trust lookup)
    verify_res = await client.get(f"/api/v1/public/verify/{verification_code}")
    assert verify_res.status_code == 200
    v_data = verify_res.json()["data"]
    assert v_data["valid"] is True
    assert v_data["certificate"]["recipient_name"] == "Sarah Connor"
    assert v_data["certificate"]["certificate_number"] == sarah_cert["certificate_number"]
    # Verify recipient email address is strictly redacted from public endpoint for privacy
    assert "sarah.connor@cyberdyne.org" not in verify_res.text

    # 10. PDF Download Check
    download_res = await client.get(f"/api/v1/certificates/{cert_id}/pdf", headers=headers)
    assert download_res.status_code == 200
    assert download_res.headers.get("Content-Type") == "application/pdf"
    assert download_res.content.startswith(b"%PDF")
