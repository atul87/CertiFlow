import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_my_organization(client: AsyncClient, registered_user):
    response = await client.get("/api/v1/organizations/me", headers=registered_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["id"] == registered_user["organization"]["id"]
    assert data["name"] == registered_user["organization"]["name"]
    assert data["slug"] == registered_user["organization"]["slug"]


@pytest.mark.asyncio
async def test_update_my_organization(client: AsyncClient, registered_user):
    new_name = "Allenhouse Institute of Technology"
    response = await client.patch(
        "/api/v1/organizations/me",
        headers=registered_user["headers"],
        json={"name": new_name}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == new_name

    # Confirm persistence
    fetch_resp = await client.get("/api/v1/organizations/me", headers=registered_user["headers"])
    assert fetch_resp.json()["data"]["name"] == new_name


@pytest.mark.asyncio
async def test_list_organization_members(client: AsyncClient, registered_user):
    response = await client.get("/api/v1/organizations/me/members", headers=registered_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    members = body["data"]
    assert len(members) == 1
    assert members[0]["role"] == "owner"
    assert members[0]["user_id"] == registered_user["user"]["id"]
    assert members[0]["user"]["email"] == registered_user["user"]["email"]


@pytest.mark.asyncio
async def test_multi_tenant_isolation(client: AsyncClient, registered_user):
    # Register a second distinct user & organization
    user_b_payload = {
        "name": "User Bravo",
        "email": "userbravo@example.com",
        "password": "PasswordBravo123"
    }
    resp_b = await client.post("/api/v1/auth/register", json=user_b_payload)
    assert resp_b.status_code == 201
    data_b = resp_b.json()["data"]
    headers_b = {"Authorization": f"Bearer {data_b['access_token']}"}

    # Verify User A gets Org A
    resp_a = await client.get("/api/v1/organizations/me", headers=registered_user["headers"])
    assert resp_a.json()["data"]["id"] == registered_user["organization"]["id"]

    # Verify User B gets Org B
    resp_b_org = await client.get("/api/v1/organizations/me", headers=headers_b)
    assert resp_b_org.json()["data"]["id"] == data_b["organization"]["id"]

    # Organizations must be strictly distinct
    assert resp_a.json()["data"]["id"] != resp_b_org.json()["data"]["id"]
    assert resp_a.json()["data"]["slug"] != resp_b_org.json()["data"]["slug"]
