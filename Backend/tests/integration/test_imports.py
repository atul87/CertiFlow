import io
import pytest
import openpyxl
from httpx import AsyncClient


def create_sample_csv() -> bytes:
    csv_text = """Name,Email Address,Course,Completion Date
Atul Kumar,atul@example.com,Python Mastery,2026-09-28
Rahul Sharma,rahul@example.com,Python Mastery,2026-09-28
Priya Singh,priya@example.com,Python Mastery,2026-09-28
"""
    return csv_text.strip().encode("utf-8")


def create_sample_xlsx() -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Student Name", "Contact Mail", "Program", "Award Date"])
    ws.append(["Alex Mercer", "alex@example.com", "Cybersecurity", "2026-09-28"])
    ws.append(["Dana Scully", "dana@example.com", "Cybersecurity", "2026-09-28"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_csv_upload_and_auto_mapping(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create a template
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Import Test Template"})
    assert t_resp.status_code == 201
    template_id = t_resp.json()["data"]["id"]

    # 2. Upload CSV
    csv_bytes = create_sample_csv()
    files = {"file": ("students.csv", csv_bytes, "text/csv")}
    data = {"template_id": template_id}

    up_resp = await client.post("/api/v1/imports", headers=headers, files=files, data=data)
    assert up_resp.status_code == 201
    imp_data = up_resp.json()["data"]

    assert imp_data["filename"] == "students.csv"
    assert imp_data["file_type"] == "csv"
    assert imp_data["total_rows"] == 3
    assert imp_data["status"] == "mapping_required"
    assert "Name" in imp_data["columns"]
    assert "Email Address" in imp_data["columns"]

    # 3. Check auto-mapping suggestions
    import_id = imp_data["id"]
    map_resp = await client.get(f"/api/v1/imports/{import_id}/mapping", headers=headers)
    assert map_resp.status_code == 200
    mappings = map_resp.json()["data"]["mappings"]

    mapped_fields = {m["target_field"]: m["source_column"] for m in mappings if m.get("source_column")}
    assert mapped_fields.get("recipient_name") == "Name"
    assert mapped_fields.get("recipient_email") == "Email Address"


@pytest.mark.asyncio
async def test_confirm_mapping_to_ready(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create template and upload CSV
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Ready Flow Template"})
    template_id = t_resp.json()["data"]["id"]

    csv_bytes = create_sample_csv()
    files = {"file": ("students.csv", csv_bytes, "text/csv")}
    data = {"template_id": template_id}
    up_resp = await client.post("/api/v1/imports", headers=headers, files=files, data=data)
    import_id = up_resp.json()["data"]["id"]

    # 2. Confirm mappings
    confirm_payload = {
        "mappings": [
            {"source_column": "Name", "target_field": "recipient_name"},
            {"source_column": "Email Address", "target_field": "recipient_email"},
            {"source_column": "Course", "target_field": "program_name"},
            {"source_column": "Completion Date", "target_field": "issue_date"}
        ]
    }
    confirm_resp = await client.post(
        f"/api/v1/imports/{import_id}/mapping",
        headers=headers,
        json=confirm_payload
    )
    assert confirm_resp.status_code == 200
    res_data = confirm_resp.json()["data"]

    # Clean dataset should immediately transition to READY!
    assert res_data["status"] == "ready"
    assert res_data["total_rows"] == 3
    assert res_data["valid_rows"] == 3
    assert res_data["invalid_rows"] == 0

    # 3. Check preview endpoint
    prev_resp = await client.get(f"/api/v1/imports/{import_id}/preview", headers=headers)
    assert prev_resp.status_code == 200
    prev_data = prev_resp.json()["data"]
    assert prev_data["summary"]["valid"] == 3
    assert len(prev_data["preview_rows"]) == 3
    assert prev_data["preview_rows"][0]["data"]["recipient_name"] == "Atul Kumar"


@pytest.mark.asyncio
async def test_validation_errors_and_error_report(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Errors Template"})
    template_id = t_resp.json()["data"]["id"]

    # CSV with 1 invalid email and 1 missing name
    err_csv = """Name,Email Address,Course,Date
Atul Kumar,atul@example.com,Python,2026-09-28
,missingname@example.com,Python,2026-09-28
Rahul Sharma,bad-email-syntax,Python,2026-09-28
"""
    files = {"file": ("err.csv", err_csv.strip().encode("utf-8"), "text/csv")}
    up_resp = await client.post("/api/v1/imports", headers=headers, files=files, data={"template_id": template_id})
    import_id = up_resp.json()["data"]["id"]

    # Confirm mapping
    confirm_payload = {
        "mappings": [
            {"source_column": "Name", "target_field": "recipient_name"},
            {"source_column": "Email Address", "target_field": "recipient_email"},
            {"source_column": "Course", "target_field": "program_name"},
            {"source_column": "Date", "target_field": "issue_date"}
        ]
    }
    c_resp = await client.post(f"/api/v1/imports/{import_id}/mapping", headers=headers, json=confirm_payload)
    res_data = c_resp.json()["data"]

    # Status must be 'validated' (not ready) because invalid_rows > 0
    assert res_data["status"] == "validated"
    assert res_data["valid_rows"] == 1
    assert res_data["invalid_rows"] == 2

    # Verify JSON errors endpoint
    err_resp = await client.get(f"/api/v1/imports/{import_id}/errors", headers=headers)
    assert err_resp.status_code == 200
    err_list = err_resp.json()["data"]
    assert len(err_list) == 2

    # Verify CSV error report download
    dl_resp = await client.get(f"/api/v1/imports/{import_id}/errors/download", headers=headers)
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "text/csv; charset=utf-8"
    csv_text = dl_resp.text
    assert "Row Number" in csv_text
    assert "MISSING_REQUIRED_FIELD" in csv_text
    assert "INVALID_EMAIL" in csv_text


@pytest.mark.asyncio
async def test_excel_upload_and_validation(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Excel Template"})
    template_id = t_resp.json()["data"]["id"]

    xlsx_bytes = create_sample_xlsx()
    files = {"file": ("students.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    up_resp = await client.post("/api/v1/imports", headers=headers, files=files, data={"template_id": template_id})
    assert up_resp.status_code == 201
    import_id = up_resp.json()["data"]["id"]

    confirm_payload = {
        "mappings": [
            {"source_column": "Student Name", "target_field": "recipient_name"},
            {"source_column": "Contact Mail", "target_field": "recipient_email"},
            {"source_column": "Program", "target_field": "program_name"},
            {"source_column": "Award Date", "target_field": "issue_date"}
        ]
    }
    c_resp = await client.post(f"/api/v1/imports/{import_id}/mapping", headers=headers, json=confirm_payload)
    assert c_resp.json()["data"]["status"] == "ready"
    assert c_resp.json()["data"]["valid_rows"] == 2


@pytest.mark.asyncio
async def test_mapping_profiles(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    profile_payload = {
        "name": "Standard College CSV Mapping",
        "mappings": [
            {"source_column": "Student Name", "target_field": "recipient_name"},
            {"source_column": "Student Email", "target_field": "recipient_email"}
        ]
    }
    create_resp = await client.post("/api/v1/mapping-profiles", headers=headers, json=profile_payload)
    assert create_resp.status_code == 201
    pid = create_resp.json()["data"]["id"]

    list_resp = await client.get("/api/v1/mapping-profiles", headers=headers)
    assert list_resp.status_code == 200
    assert any(p["id"] == pid for p in list_resp.json()["data"])

    del_resp = await client.delete(f"/api/v1/mapping-profiles/{pid}", headers=headers)
    assert del_resp.status_code == 200


@pytest.mark.asyncio
async def test_multi_tenant_import_isolation(client: AsyncClient, registered_user):
    headers_a = registered_user["headers"]

    # Register Org B
    resp_b = await client.post("/api/v1/auth/register", json={
        "name": "Org B User",
        "email": "orgb.imports@example.com",
        "password": "PasswordOrgB123"
    })
    headers_b = {"Authorization": f"Bearer {resp_b.json()['data']['access_token']}"}

    # Org A creates template & import
    t_resp = await client.post("/api/v1/templates", headers=headers_a, json={"name": "Org A Template"})
    t_id = t_resp.json()["data"]["id"]

    csv_bytes = create_sample_csv()
    files = {"file": ("students.csv", csv_bytes, "text/csv")}
    up_resp = await client.post("/api/v1/imports", headers=headers_a, files=files, data={"template_id": t_id})
    imp_id = up_resp.json()["data"]["id"]

    # Org B attempts to access Org A import -> 404 NOT_FOUND
    get_resp = await client.get(f"/api/v1/imports/{imp_id}", headers=headers_b)
    assert get_resp.status_code == 404
    assert get_resp.json()["error"]["code"] == "IMPORT_NOT_FOUND"

    # Org B attempts to read errors of Org A import -> 404 NOT_FOUND
    err_resp = await client.get(f"/api/v1/imports/{imp_id}/errors", headers=headers_b)
    assert err_resp.status_code == 404


@pytest.mark.asyncio
async def test_full_e2e_p0_to_p2_flow(client: AsyncClient):
    # 1. Register User & Org (P0)
    reg_resp = await client.post("/api/v1/auth/register", json={
        "name": "Prof. Albus Dumbledore",
        "email": "headmaster@hogwarts.edu",
        "password": "ElderWandPassword2026"
    })
    assert reg_resp.status_code == 201
    auth_data = reg_resp.json()["data"]
    headers = {"Authorization": f"Bearer {auth_data['access_token']}"}

    # 2. Create Certificate Template & Publish Version 1 (P1)
    t_resp = await client.post("/api/v1/templates", headers=headers, json={
        "name": "Defense Against the Dark Arts Diploma",
        "description": "Annual graduation award"
    })
    assert t_resp.status_code == 201
    template_id = t_resp.json()["data"]["id"]
    version_id = t_resp.json()["data"]["current_version_id"]

    pub_resp = await client.post(f"/api/v1/templates/{template_id}/versions/{version_id}/publish", headers=headers)
    assert pub_resp.status_code == 200
    assert pub_resp.json()["data"]["status"] == "published"

    # 3. Upload Recipient CSV (P2)
    students_csv = """Candidate Name,Contact Email,House Subject,Date of Graduation
Harry Potter,harry@hogwarts.edu,Defense Against the Dark Arts,2026-06-30
Hermione Granger,hermione@hogwarts.edu,Defense Against the Dark Arts,2026-06-30
Ron Weasley,ron@hogwarts.edu,Defense Against the Dark Arts,2026-06-30
"""
    files = {"file": ("graduates.csv", students_csv.strip().encode("utf-8"), "text/csv")}
    up_resp = await client.post("/api/v1/imports", headers=headers, files=files, data={"template_id": template_id})
    assert up_resp.status_code == 201
    import_id = up_resp.json()["data"]["id"]
    assert up_resp.json()["data"]["status"] == "mapping_required"

    # 4. Map columns & Validate
    mapping_payload = {
        "mappings": [
            {"source_column": "Candidate Name", "target_field": "recipient_name"},
            {"source_column": "Contact Email", "target_field": "recipient_email"},
            {"source_column": "House Subject", "target_field": "program_name"},
            {"source_column": "Date of Graduation", "target_field": "issue_date"}
        ]
    }
    c_resp = await client.post(f"/api/v1/imports/{import_id}/mapping", headers=headers, json=mapping_payload)
    assert c_resp.status_code == 200
    final_import = c_resp.json()["data"]

    # P2 GOAL VERIFIED: Status is READY for P3 Certificate Rendering Engine!
    assert final_import["status"] == "ready"
    assert final_import["total_rows"] == 3
    assert final_import["valid_rows"] == 3
    assert final_import["invalid_rows"] == 0
