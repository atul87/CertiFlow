import pytest
import asyncio
from httpx import AsyncClient

from app.workers.email_worker import send_certificate_email_task, process_bulk_email_job_task
from app.services.signed_url_service import SignedUrlService
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.repositories.email_job_repository import EmailJobRepository
from app.repositories.email_suppression_repository import EmailSuppressionRepository


async def create_published_template_and_certificate(client: AsyncClient, headers: dict, recipient_email: str = "atul@example.com") -> dict:
    # 1. Create template
    t_resp = await client.post(
        "/api/v1/templates",
        headers=headers,
        json={"name": "Email Cert Template"}
    )
    assert t_resp.status_code == 201
    template_id = t_resp.json()["data"]["id"]
    version_id = t_resp.json()["data"]["current_version_id"]

    # 2. Publish template version
    pub_resp = await client.post(
        f"/api/v1/templates/{template_id}/versions/{version_id}/publish",
        headers=headers,
    )
    assert pub_resp.status_code == 200

    # 3. Generate certificate
    gen_payload = {
        "template_version_id": version_id,
        "data": {
            "recipient_name": "Atul Kumar",
            "recipient_email": recipient_email,
            "program_name": "Email Architecture Mastery",
            "issue_date": "28 September 2026",
        }
    }
    gen_resp = await client.post("/api/v1/certificates/generate", headers=headers, json=gen_payload)
    assert gen_resp.status_code == 201
    return gen_resp.json()["data"]


@pytest.mark.asyncio
async def test_email_template_crud(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create template
    payload = {
        "name": "Course Completion Email",
        "subject": "Congratulations {{recipient_name}} on completing {{program_name}}!",
        "html_body": "<h2>Hello {{recipient_name}}</h2><p>Verify here: {{verification_url}}</p>",
    }
    create_resp = await client.post("/api/v1/email/templates", headers=headers, json=payload)
    assert create_resp.status_code == 201
    tpl = create_resp.json()["data"]
    assert tpl["name"] == payload["name"]
    assert "recipient_name" in tpl["variables"]
    assert "verification_url" in tpl["variables"]
    tpl_id = tpl["id"]

    # 2. List templates
    list_resp = await client.get("/api/v1/email/templates", headers=headers)
    assert list_resp.status_code == 200
    assert any(t["id"] == tpl_id for t in list_resp.json()["data"]["items"])

    # 3. Get template
    get_resp = await client.get(f"/api/v1/email/templates/{tpl_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == tpl_id

    # 4. Update template
    upd_payload = {"name": "Updated Email Template"}
    upd_resp = await client.put(f"/api/v1/email/templates/{tpl_id}", headers=headers, json=upd_payload)
    assert upd_resp.status_code == 200
    assert upd_resp.json()["data"]["name"] == "Updated Email Template"

    # 5. Delete template
    del_resp = await client.delete(f"/api/v1/email/templates/{tpl_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_email_settings_and_masking(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Get default settings
    get_resp = await client.get("/api/v1/email/settings", headers=headers)
    assert get_resp.status_code == 200
    data = get_resp.json()["data"]
    assert "provider" in data
    assert data["has_smtp_password"] is False

    # 2. Update settings with secrets
    upd_payload = {
        "provider": "smtp",
        "sender_name": "Masterclass Institute",
        "sender_email": "certs@masterclass.org",
        "smtp_host": "smtp.mailgun.org",
        "smtp_port": 587,
        "smtp_username": "postmaster@masterclass.org",
        "smtp_password": "supersecretpassword123",
        "api_key": "api_key_secret_999",
        "auto_email_on_issuance": True,
    }
    upd_resp = await client.put("/api/v1/email/settings", headers=headers, json=upd_payload)
    assert upd_resp.status_code == 200
    res_data = upd_resp.json()["data"]

    # Security check: secrets must NEVER be returned in response!
    assert "supersecretpassword123" not in upd_resp.text
    assert "api_key_secret_999" not in upd_resp.text
    assert res_data["has_smtp_password"] is True
    assert res_data["has_api_key"] is True
    assert res_data["sender_name"] == "Masterclass Institute"
    assert res_data["auto_email_on_issuance"] is True


@pytest.mark.asyncio
async def test_email_preview_and_test_send(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # Preview email
    prev_payload = {
        "subject": "Cert for {{recipient_name}}",
        "html_body": "<p>Hello {{recipient_name}}, here is {{certificate_number}}.</p>",
    }
    prev_resp = await client.post("/api/v1/email/preview", headers=headers, json=prev_payload)
    assert prev_resp.status_code == 200
    preview = prev_resp.json()["data"]
    assert "Atul Kumar" in preview["subject"] or "CERT" in preview["html"]

    # Test send
    test_payload = {
        "recipient_email": "tester@example.com",
    }
    test_resp = await client.post("/api/v1/email/test", headers=headers, json=test_payload)
    assert test_resp.status_code == 200
    assert test_resp.json()["data"]["success"] is True


@pytest.mark.asyncio
async def test_single_certificate_email_delivery_and_resend(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers)
    cert_id = cert["id"]

    # 1. Send certificate email
    send_resp = await client.post(f"/api/v1/certificates/{cert_id}/email", headers=headers, json={"delivery_mode": "link"})
    assert send_resp.status_code == 201
    delivery = send_resp.json()["data"]
    delivery_id = delivery["id"]
    assert delivery["status"] == "queued"
    assert delivery["certificate_id"] == cert_id

    # Process task via email worker
    worker_res = await send_certificate_email_task(None, delivery_id)
    assert worker_res is not None
    assert worker_res["status"] == "sent"

    # Check delivery details
    det_resp = await client.get(f"/api/v1/email-deliveries/{delivery_id}", headers=headers)
    assert det_resp.status_code == 200
    det = det_resp.json()["data"]
    assert det["status"] == "sent"
    assert len(det["events"]) >= 1

    # 2. Resend certificate email
    resend_resp = await client.post(f"/api/v1/certificates/{cert_id}/resend-email", headers=headers, json={"delivery_mode": "both"})
    assert resend_resp.status_code == 201
    resend_delivery = resend_resp.json()["data"]
    assert resend_delivery["id"] != delivery_id  # Auditable new record
    assert resend_delivery["status"] == "queued"


@pytest.mark.asyncio
async def test_bulk_email_job_processing(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert1 = await create_published_template_and_certificate(client, headers, "student1@example.com")
    cert2 = await create_published_template_and_certificate(client, headers, "student2@example.com")

    # 1. Create bulk email job
    job_payload = {
        "certificate_ids": [cert1["id"], cert2["id"]],
        "delivery_mode": "link",
    }
    job_resp = await client.post("/api/v1/email-jobs", headers=headers, json=job_payload)
    assert job_resp.status_code == 201
    job = job_resp.json()["data"]
    job_id = job["id"]
    assert job["total"] == 2
    assert job["status"] == "queued"

    # 2. Process bulk email job worker
    org_id = registered_user["organization"]["id"]
    final_job = await process_bulk_email_job_task(None, job_id, org_id)
    assert final_job is not None
    assert final_job["sent"] == 2
    assert final_job["status"] == "completed"

    # 3. Check progress endpoint
    prog_resp = await client.get(f"/api/v1/email-jobs/{job_id}/progress", headers=headers)
    assert prog_resp.status_code == 200
    prog = prog_resp.json()["data"]
    assert prog["sent"] == 2
    assert prog["progress_percentage"] == 100.0


@pytest.mark.asyncio
async def test_provider_webhooks_and_suppression(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers, "bouncy@example.com")

    # 1. Send certificate email
    send_resp = await client.post(f"/api/v1/certificates/{cert['id']}/email", headers=headers)
    assert send_resp.status_code == 201
    deliv_id = send_resp.json()["data"]["id"]

    # Process send
    sent_doc = await send_certificate_email_task(None, deliv_id)
    provider_msg_id = sent_doc["provider_message_id"]

    # 2. Webhook: simulate delivered
    webhook_payload_delivered = {
        "event": "delivered",
        "message_id": provider_msg_id,
        "event_id": "evt_dlv_123",
    }
    wh_resp = await client.post("/api/v1/webhooks/email/mock", json=webhook_payload_delivered)
    assert wh_resp.status_code == 200
    assert wh_resp.json()["processed"] is True

    deliv_after_wh = await EmailDeliveryRepository.get_by_id(deliv_id)
    assert deliv_after_wh["status"] == "delivered"

    # 3. Idempotent webhook check: same event sent again
    wh_dup_resp = await client.post("/api/v1/webhooks/email/mock", json=webhook_payload_delivered)
    assert wh_dup_resp.status_code == 200

    # 4. Webhook: simulate bounce on another certificate email
    cert_bounce = await create_published_template_and_certificate(client, headers, "badrecipient@example.com")
    send_bounce = await client.post(f"/api/v1/certificates/{cert_bounce['id']}/email", headers=headers)
    deliv_bounce_id = send_bounce.json()["data"]["id"]
    sent_bounce_doc = await send_certificate_email_task(None, deliv_bounce_id)

    bounce_webhook = {
        "event": "bounced",
        "message_id": sent_bounce_doc["provider_message_id"],
        "event_id": "evt_bnc_456",
        "reason": "550 Mailbox does not exist",
    }
    wh_bnc_resp = await client.post("/api/v1/webhooks/email/mock", json=bounce_webhook)
    assert wh_bnc_resp.status_code == 200

    deliv_bounced = await EmailDeliveryRepository.get_by_id(deliv_bounce_id)
    assert deliv_bounced["status"] == "bounced"

    # Verify recipient was added to suppression list
    org_id = registered_user["organization"]["id"]
    is_suppressed = await EmailSuppressionRepository.is_suppressed(org_id, "badrecipient@example.com")
    assert is_suppressed is True

    # 5. Sending to suppressed recipient fails immediately with EMAIL_SUPPRESSED
    cert_suppressed = await create_published_template_and_certificate(client, headers, "badrecipient@example.com")
    send_suppressed = await client.post(f"/api/v1/certificates/{cert_suppressed['id']}/email", headers=headers)
    deliv_suppressed_id = send_suppressed.json()["data"]["id"]

    processed_suppressed = await send_certificate_email_task(None, deliv_suppressed_id)
    assert processed_suppressed["status"] == "failed"
    assert processed_suppressed["error"]["error_code"] == "EMAIL_SUPPRESSED"


@pytest.mark.asyncio
async def test_signed_download_url(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers)
    code = cert["verification_code"]

    # Generate signed token
    token = SignedUrlService.generate_token(code, expires_in_seconds=3600)

    # Public download using token
    dl_resp = await client.get(f"/api/v1/public/certificates/{code}/download?token={token}")
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"
    assert len(dl_resp.content) > 0
