import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_certificates_empty(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    response = await client.get("/api/v1/certificates", headers=headers)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert body["data"]["total"] == 0
    assert body["data"]["items"] == []


@pytest.mark.asyncio
async def test_list_certificates_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/certificates")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_nonexistent_certificate(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    fake_id = "65a000000000000000000000"
    response = await client.get(f"/api/v1/certificates/{fake_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_revoke_nonexistent_certificate(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    fake_id = "65a000000000000000000000"
    payload = {"reason": "Issued in error"}
    response = await client.post(
        f"/api/v1/certificates/{fake_id}/revoke",
        headers=headers,
        json=payload
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_verify_nonexistent_certificate_code(client: AsyncClient):
    fake_code = "CERT-NONEXISTENT-999"
    response = await client.get(f"/api/v1/verify/{fake_code}")
    assert response.status_code == 200
    res = response.json()
    assert res.get("valid") is False
