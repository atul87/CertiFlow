import pytest
from httpx import AsyncClient
from tests.integration.test_imports import create_sample_csv


async def setup_published_template_and_ready_import(client: AsyncClient, headers: dict):
    # 1. Create template
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Bulk Issuance Template"})
    assert t_resp.status_code == 201
    template_id = t_resp.json()["data"]["id"]
    version_id = t_resp.json()["data"]["current_version_id"]

    # 2. Publish template version
    pub_resp = await client.post(
        f"/api/v1/templates/{template_id}/versions/{version_id}/publish",
        headers=headers,
    )
    assert pub_resp.status_code == 200

    # 3. Upload CSV
    csv_bytes = create_sample_csv()
    files = {"file": ("students.csv", csv_bytes, "text/csv")}
    data = {"template_id": template_id}
    up_resp = await client.post("/api/v1/imports", headers=headers, files=files, data=data)
    assert up_resp.status_code == 201
    import_id = up_resp.json()["data"]["id"]

    # 4. Confirm mapping to bring import to 'ready'
    confirm_payload = {
        "mappings": [
            {"source_column": "Name", "target_field": "recipient_name"},
            {"source_column": "Email Address", "target_field": "recipient_email"},
            {"source_column": "Course", "target_field": "program_name"},
            {"source_column": "Completion Date", "target_field": "issue_date"},
        ]
    }
    confirm_resp = await client.post(
        f"/api/v1/imports/{import_id}/mapping",
        headers=headers,
        json=confirm_payload,
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["data"]["status"] == "ready"

    return template_id, version_id, import_id


@pytest.mark.asyncio
async def test_create_issuance_job_success(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    template_id, version_id, import_id = await setup_published_template_and_ready_import(client, headers)

    # Create Issuance Job
    payload = {
        "import_id": import_id,
        "template_version_id": version_id,
    }
    response = await client.post("/api/v1/issuance-jobs", headers=headers, json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["success"] is True
    job_data = body["data"]

    assert job_data["status"] == "queued"
    assert job_data["total"] == 3
    assert job_data["pending"] == 3
    assert job_data["template_id"] == template_id
    assert job_data["template_version_id"] == version_id
    assert job_data["import_id"] == import_id
    assert "id" in job_data


@pytest.mark.asyncio
async def test_create_issuance_job_validations(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Non-existent import
    bad_import_payload = {
        "import_id": "60d5ec49f1b2c8b1f8e4e1a1",
        "template_version_id": "60d5ec49f1b2c8b1f8e4e1a2",
    }
    res = await client.post("/api/v1/issuance-jobs", headers=headers, json=bad_import_payload)
    assert res.status_code in (404, 422)

    # 2. Template version is draft (not published)
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Draft Template"})
    draft_version_id = t_resp.json()["data"]["current_version_id"]

    # Upload CSV for draft template
    csv_bytes = create_sample_csv()
    files = {"file": ("students.csv", csv_bytes, "text/csv")}
    up_resp = await client.post("/api/v1/imports", headers=headers, files=files, data={"template_id": t_resp.json()["data"]["id"]})
    imp_id = up_resp.json()["data"]["id"]

    draft_payload = {
        "import_id": imp_id,
        "template_version_id": draft_version_id,
    }
    res_draft = await client.post("/api/v1/issuance-jobs", headers=headers, json=draft_payload)
    assert res_draft.status_code == 422
    assert res_draft.json()["error"]["code"] == "TEMPLATE_NOT_PUBLISHED"


@pytest.mark.asyncio
async def test_get_and_list_issuance_jobs(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    _, version_id, import_id = await setup_published_template_and_ready_import(client, headers)

    create_resp = await client.post(
        "/api/v1/issuance-jobs",
        headers=headers,
        json={"import_id": import_id, "template_version_id": version_id},
    )
    job_id = create_resp.json()["data"]["id"]

    # Get single job
    get_resp = await client.get(f"/api/v1/issuance-jobs/{job_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == job_id

    # List jobs
    list_resp = await client.get("/api/v1/issuance-jobs", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()["data"]
    assert list_data["total"] >= 1
    assert any(j["id"] == job_id for j in list_data["items"])


@pytest.mark.asyncio
async def test_job_progress_and_items(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    _, version_id, import_id = await setup_published_template_and_ready_import(client, headers)

    create_resp = await client.post(
        "/api/v1/issuance-jobs",
        headers=headers,
        json={"import_id": import_id, "template_version_id": version_id},
    )
    job_id = create_resp.json()["data"]["id"]

    # Check progress
    prog_resp = await client.get(f"/api/v1/issuance-jobs/{job_id}/progress", headers=headers)
    assert prog_resp.status_code == 200
    prog_data = prog_resp.json()["data"]
    assert prog_data["job_id"] == job_id
    assert prog_data["total"] == 3
    assert "progress" in prog_data

    # List items
    items_resp = await client.get(f"/api/v1/issuance-jobs/{job_id}/items", headers=headers)
    assert items_resp.status_code == 200
    items_data = items_resp.json()["data"]
    assert items_data["total"] == 3
    assert len(items_data["items"]) == 3
    assert items_data["items"][0]["row_number"] == 1


@pytest.mark.asyncio
async def test_job_lifecycle_pause_resume_cancel(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    _, version_id, import_id = await setup_published_template_and_ready_import(client, headers)

    create_resp = await client.post(
        "/api/v1/issuance-jobs",
        headers=headers,
        json={"import_id": import_id, "template_version_id": version_id},
    )
    job_id = create_resp.json()["data"]["id"]

    # Pause
    pause_resp = await client.post(f"/api/v1/issuance-jobs/{job_id}/pause", headers=headers)
    assert pause_resp.status_code == 200
    assert pause_resp.json()["data"]["status"] == "paused"

    # Resume
    resume_resp = await client.post(f"/api/v1/issuance-jobs/{job_id}/resume", headers=headers)
    assert resume_resp.status_code == 200
    assert resume_resp.json()["data"]["status"] == "queued"

    # Cancel
    cancel_resp = await client.post(f"/api/v1/issuance-jobs/{job_id}/cancel", headers=headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["data"]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_errors_report_and_csv_download(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    _, version_id, import_id = await setup_published_template_and_ready_import(client, headers)

    create_resp = await client.post(
        "/api/v1/issuance-jobs",
        headers=headers,
        json={"import_id": import_id, "template_version_id": version_id},
    )
    job_id = create_resp.json()["data"]["id"]

    # Get errors (currently empty as all are pending)
    err_resp = await client.get(f"/api/v1/issuance-jobs/{job_id}/errors", headers=headers)
    assert err_resp.status_code == 200
    assert isinstance(err_resp.json()["data"], list)

    # Download errors CSV
    csv_resp = await client.get(f"/api/v1/issuance-jobs/{job_id}/errors/download", headers=headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "row_number,recipient_name,email,error_code,error_message,attempts" in csv_resp.text


@pytest.mark.asyncio
async def test_zip_export_status(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    _, version_id, import_id = await setup_published_template_and_ready_import(client, headers)

    create_resp = await client.post(
        "/api/v1/issuance-jobs",
        headers=headers,
        json={"import_id": import_id, "template_version_id": version_id},
    )
    job_id = create_resp.json()["data"]["id"]

    # Request ZIP
    zip_resp = await client.post(f"/api/v1/issuance-jobs/{job_id}/zip", headers=headers)
    assert zip_resp.status_code == 200
    assert zip_resp.json()["data"]["status"] in ("queued", "processing", "ready", "failed")

    # Check ZIP status
    status_resp = await client.get(f"/api/v1/issuance-jobs/{job_id}/zip", headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["data"]["job_id"] == job_id
