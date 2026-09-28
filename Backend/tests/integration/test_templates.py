import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_template_auto_v1(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    payload = {
        "name": "AI Workshop Certificate",
        "description": "Completion certificate for AI engineering"
    }

    response = await client.post("/api/v1/templates", headers=headers, json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["success"] is True
    data = body["data"]

    assert data["name"] == "AI Workshop Certificate"
    assert data["status"] == "active"
    assert data["current_version_id"] is not None

    # Verify v1 draft automatically created
    v1 = data["current_version"]
    assert v1 is not None
    assert v1["version"] == 1
    assert v1["status"] == "draft"
    assert len(v1["elements"]) > 0

    # Verify extracted fields in v1
    field_keys = [f["key"] for f in v1["fields"]]
    assert "recipient_name" in field_keys
    assert "program_name" in field_keys


@pytest.mark.asyncio
async def test_list_and_search_templates(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # Create 3 templates
    await client.post("/api/v1/templates", headers=headers, json={"name": "Machine Learning Bootcamp"})
    await client.post("/api/v1/templates", headers=headers, json={"name": "Web Development Mastery"})
    await client.post("/api/v1/templates", headers=headers, json={"name": "Cybersecurity Fundamentals"})

    # List all
    resp_all = await client.get("/api/v1/templates?limit=10", headers=headers)
    assert resp_all.status_code == 200
    assert resp_all.json()["data"]["total"] >= 3

    # Search
    resp_search = await client.get("/api/v1/templates?search=Cybersecurity", headers=headers)
    assert resp_search.status_code == 200
    search_data = resp_search.json()["data"]
    assert search_data["total"] == 1
    assert search_data["items"][0]["name"] == "Cybersecurity Fundamentals"


@pytest.mark.asyncio
async def test_get_template_details(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    create_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Cloud Architecture Certificate"})
    template_id = create_resp.json()["data"]["id"]

    resp = await client.get(f"/api/v1/templates/{template_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["id"] == template_id
    assert body["data"]["name"] == "Cloud Architecture Certificate"


@pytest.mark.asyncio
async def test_update_template_metadata(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    create_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Original Name"})
    template_id = create_resp.json()["data"]["id"]

    update_resp = await client.patch(
        f"/api/v1/templates/{template_id}",
        headers=headers,
        json={"name": "Updated Name", "description": "New description"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "Updated Name"
    assert update_resp.json()["data"]["description"] == "New description"


@pytest.mark.asyncio
async def test_duplicate_template(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    create_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Python Diploma"})
    orig_id = create_resp.json()["data"]["id"]

    dup_resp = await client.post(f"/api/v1/templates/{orig_id}/duplicate", headers=headers)
    assert dup_resp.status_code == 201
    dup_data = dup_resp.json()["data"]

    assert dup_data["id"] != orig_id
    assert dup_data["name"] == "Python Diploma (Copy)"
    assert dup_data["current_version_id"] is not None
    assert dup_data["current_version"]["version"] == 1


@pytest.mark.asyncio
async def test_archive_template(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    create_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "To Be Archived"})
    template_id = create_resp.json()["data"]["id"]

    arch_resp = await client.post(f"/api/v1/templates/{template_id}/archive", headers=headers)
    assert arch_resp.status_code == 200
    assert arch_resp.json()["success"] is True

    # Confirm it is no longer returned in default active list
    list_resp = await client.get("/api/v1/templates?status=active", headers=headers)
    active_ids = [t["id"] for t in list_resp.json()["data"]["items"]]
    assert template_id not in active_ids


@pytest.mark.asyncio
async def test_version_lifecycle_and_immutability(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create template
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Lifecycle Template"})
    template_id = t_resp.json()["data"]["id"]
    version_id = t_resp.json()["data"]["current_version_id"]

    # 2. Update draft version
    new_elements = [
        {
            "id": "t1",
            "type": "text",
            "content": "Official Honor for {{recipient_name}} in {{program_name}}",
            "position": {"x": 500, "y": 800},
            "size": {"width": 2000, "height": 100},
            "style": {"font_family": "Montserrat", "font_size": 52, "color": "#000000", "alignment": "center"}
        }
    ]
    put_resp = await client.put(
        f"/api/v1/templates/{template_id}/versions/{version_id}",
        headers=headers,
        json={"elements": new_elements}
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["data"]["elements"][0]["id"] == "t1"

    # 3. Publish version
    pub_resp = await client.post(
        f"/api/v1/templates/{template_id}/versions/{version_id}/publish",
        headers=headers
    )
    assert pub_resp.status_code == 200
    assert pub_resp.json()["data"]["status"] == "published"

    # 4. IMMUTABILITY CHECK: Attempting to modify a published version MUST FAIL
    mod_resp = await client.put(
        f"/api/v1/templates/{template_id}/versions/{version_id}",
        headers=headers,
        json={"elements": new_elements}
    )
    assert mod_resp.status_code == 403
    assert mod_resp.json()["error"]["code"] == "VERSION_IMMUTABLE"


@pytest.mark.asyncio
async def test_multi_tenant_template_isolation(client: AsyncClient, registered_user):
    headers_a = registered_user["headers"]

    # Register user B
    user_b_payload = {
        "name": "Org B Admin",
        "email": "orgb.admin@example.com",
        "password": "PasswordOrgB123"
    }
    resp_b = await client.post("/api/v1/auth/register", json=user_b_payload)
    headers_b = {"Authorization": f"Bearer {resp_b.json()['data']['access_token']}"}

    # Org A creates a template
    t_resp = await client.post("/api/v1/templates", headers=headers_a, json={"name": "Org A Secret Template"})
    tmpl_id = t_resp.json()["data"]["id"]

    # Org B attempts to read Org A template -> 404 NOT_FOUND
    get_resp = await client.get(f"/api/v1/templates/{tmpl_id}", headers=headers_b)
    assert get_resp.status_code == 404
    assert get_resp.json()["error"]["code"] == "TEMPLATE_NOT_FOUND"

    # Org B attempts to modify Org A template -> 404 NOT_FOUND
    patch_resp = await client.patch(f"/api/v1/templates/{tmpl_id}", headers=headers_b, json={"name": "Hacked"})
    assert patch_resp.status_code == 404
