import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_key_lifecycle_and_authentication(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create API Key
    key_payload = {
        "name": "Integration Key",
        "scopes": ["certificates:read", "certificates:create"],
    }
    create_res = await client.post("/api/v1/api-keys", json=key_payload, headers=headers)
    assert create_res.status_code == 201
    key_data = create_res.json()["data"]
    assert "key" in key_data
    raw_api_key = key_data["key"]
    key_id = key_data["id"]
    assert raw_api_key.startswith("ck_live_")

    # 2. List API Keys (plaintext secret must not be returned)
    list_res = await client.get("/api/v1/api-keys", headers=headers)
    assert list_res.status_code == 200
    keys = list_res.json()["data"]["items"]
    assert len(keys) == 1
    assert keys[0]["key"] is None
    assert keys[0]["prefix"].startswith("ck_live_")

    # 3. Authenticate with Bearer ck_live_... on an authorized endpoint
    api_auth_headers = {"Authorization": f"Bearer {raw_api_key}"}
    cert_list_res = await client.get("/api/v1/certificates", headers=api_auth_headers)
    assert cert_list_res.status_code == 200

    # 4. Revoke API Key
    revoke_res = await client.post(f"/api/v1/api-keys/{key_id}/revoke", headers=headers)
    assert revoke_res.status_code == 200
    assert revoke_res.json()["data"]["status"] == "revoked"

    # 5. Subsequent request with revoked key must fail with 401
    fail_res = await client.get("/api/v1/certificates", headers=api_auth_headers)
    assert fail_res.status_code == 401
    assert fail_res.json()["error"]["code"] == "API_KEY_REVOKED"


@pytest.mark.asyncio
async def test_api_key_scope_enforcement(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # Create read-only key
    create_res = await client.post(
        "/api/v1/api-keys",
        json={"name": "ReadOnly Key", "scopes": ["certificates:read"]},
        headers=headers,
    )
    assert create_res.status_code == 201
    read_only_key = create_res.json()["data"]["key"]
    ro_headers = {"Authorization": f"Bearer {read_only_key}"}

    # Attempt write operation requiring "certificates.create"
    write_res = await client.post(
        "/api/v1/certificates/generate",
        json={"template_version_id": "000000000000000000000000", "data": {}},
        headers=ro_headers,
    )
    assert write_res.status_code == 403
    assert write_res.json()["error"]["code"] == "INSUFFICIENT_SCOPE"


@pytest.mark.asyncio
async def test_service_accounts_crud(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create service account
    sa_res = await client.post(
        "/api/v1/service-accounts",
        json={"name": "ERP Automation", "description": "Backend synchronization service"},
        headers=headers,
    )
    assert sa_res.status_code == 201
    sa = sa_res.json()["data"]
    sa_id = sa["id"]
    assert sa["name"] == "ERP Automation"

    # 2. List service accounts
    list_sa = await client.get("/api/v1/service-accounts", headers=headers)
    assert list_sa.status_code == 200
    assert len(list_sa.json()["data"]["items"]) == 1

    # 3. Create API Key for this service account
    key_res = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "ERP Key",
            "scopes": ["certificates:create", "certificates:read"],
            "service_account_id": sa_id,
        },
        headers=headers,
    )
    assert key_res.status_code == 201
    assert key_res.json()["data"]["service_account_id"] == sa_id

    # 4. Delete service account
    del_sa = await client.delete(f"/api/v1/service-accounts/{sa_id}", headers=headers)
    assert del_sa.status_code == 200
    assert del_sa.json()["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_webhook_endpoints_and_testing(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create webhook endpoint
    ep_payload = {
        "url": "https://example.com/webhooks/certiflow",
        "events": ["certificate.generated", "certificate.revoked"],
        "description": "Production customer webhook",
    }
    ep_res = await client.post("/api/v1/webhooks", json=ep_payload, headers=headers)
    assert ep_res.status_code == 201
    ep_data = ep_res.json()["data"]
    assert "secret" in ep_data
    assert ep_data["secret"].startswith("whsec_")
    endpoint_id = ep_data["id"]

    # 2. List endpoints (secret omitted)
    list_res = await client.get("/api/v1/webhooks", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]["items"]) == 1
    assert list_res.json()["data"]["items"][0]["secret"] is None

    # 3. Rotate secret
    rot_res = await client.post(f"/api/v1/webhooks/{endpoint_id}/rotate-secret", headers=headers)
    assert rot_res.status_code == 200
    assert rot_res.json()["data"]["secret"] != ep_data["secret"]

    # 4. List deliveries
    deliv_res = await client.get(f"/api/v1/webhooks/{endpoint_id}/deliveries", headers=headers)
    assert deliv_res.status_code == 200
    assert "items" in deliv_res.json()["data"]


@pytest.mark.asyncio
async def test_api_usage_metrics(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    res = await client.get("/api/v1/api-usage?days=7", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "total_requests" in data
    assert "successful_2xx" in data
    assert "average_latency_ms" in data
