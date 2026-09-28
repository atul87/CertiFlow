import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_member_invitation_and_acceptance(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Invite a new member
    invite_payload = {
        "email": "colleague@example.com",
        "role": "admin",
        "expires_in_days": 7,
    }
    invite_res = await client.post("/api/v1/organization/invitations", json=invite_payload, headers=headers)
    assert invite_res.status_code == 201
    invite_data = invite_res.json()["data"]
    assert invite_data["email"] == "colleague@example.com"
    assert invite_data["role"] == "admin"
    assert invite_data["status"] == "pending"
    assert "invitation_token" in invite_data
    token = invite_data["invitation_token"]

    # 2. List invitations
    list_inv = await client.get("/api/v1/organization/invitations", headers=headers)
    assert list_inv.status_code == 200
    assert list_inv.json()["data"]["total"] >= 1

    # 3. Accept invitation
    accept_payload = {
        "token": token,
        "name": "Colleague Name",
        "password": "ColleaguePassword123",
    }
    accept_res = await client.post("/api/v1/organization/invitations/accept", json=accept_payload)
    assert accept_res.status_code == 200
    accept_data = accept_res.json()["data"]
    assert "access_token" in accept_data
    colleague_headers = {"Authorization": f"Bearer {accept_data['access_token']}"}

    # 4. List members as owner
    members_res = await client.get("/api/v1/organization/members", headers=headers)
    assert members_res.status_code == 200
    members = members_res.json()["data"]["items"]
    assert len(members) == 2
    emails = [m["user"]["email"] for m in members if m.get("user")]
    assert "colleague@example.com" in emails


@pytest.mark.asyncio
async def test_role_permission_enforcement(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Invite a viewer
    invite_res = await client.post(
        "/api/v1/organization/invitations",
        json={"email": "viewer@example.com", "role": "viewer"},
        headers=headers,
    )
    token = invite_res.json()["data"]["invitation_token"]

    # 2. Accept invite
    accept_res = await client.post(
        "/api/v1/organization/invitations/accept",
        json={"token": token, "name": "Viewer User", "password": "ViewerPassword123"},
    )
    viewer_headers = {"Authorization": f"Bearer {accept_res.json()['data']['access_token']}"}

    # 3. Viewer attempts to invite another user -> 403 Forbidden
    unauth_invite = await client.post(
        "/api/v1/organization/invitations",
        json={"email": "someone@example.com", "role": "member"},
        headers=viewer_headers,
    )
    assert unauth_invite.status_code == 403
    assert unauth_invite.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


@pytest.mark.asyncio
async def test_custom_roles_lifecycle(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Get permission registry
    reg_res = await client.get("/api/v1/roles/permissions/registry", headers=headers)
    assert reg_res.status_code == 200
    assert "certificates.create" in reg_res.json()["data"]

    # 2. Create custom role
    role_payload = {
        "name": "CertManager",
        "description": "Can manage certificates and templates",
        "permissions": ["certificates.read", "certificates.create", "templates.read"],
    }
    create_res = await client.post("/api/v1/roles", json=role_payload, headers=headers)
    assert create_res.status_code == 201
    role_id = create_res.json()["data"]["id"]

    # 3. List roles includes custom role
    roles_res = await client.get("/api/v1/roles", headers=headers)
    assert roles_res.status_code == 200
    role_names = [r["name"] for r in roles_res.json()["data"]["items"]]
    assert "CertManager" in role_names

    # 4. Delete custom role
    del_res = await client.delete(f"/api/v1/roles/{role_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_member_suspension_and_blocking(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # Invite and accept
    inv = await client.post(
        "/api/v1/organization/invitations",
        json={"email": "operator@example.com", "role": "member"},
        headers=headers,
    )
    token = inv.json()["data"]["invitation_token"]

    acc = await client.post(
        "/api/v1/organization/invitations/accept",
        json={"token": token, "name": "Operator", "password": "Password123"},
    )
    op_headers = {"Authorization": f"Bearer {acc.json()['data']['access_token']}"}

    # Find member ID
    members_res = await client.get("/api/v1/organization/members", headers=headers)
    members = members_res.json()["data"]["items"]
    op_member = next(m for m in members if m.get("user") and m["user"]["email"] == "operator@example.com")
    op_member_id = op_member["id"]

    # Suspend member
    patch_res = await client.patch(
        f"/api/v1/organization/members/{op_member_id}",
        json={"status": "suspended"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "suspended"

    # Suspended member requests must be blocked with 403
    blocked_req = await client.get("/api/v1/organizations/me", headers=op_headers)
    assert blocked_req.status_code == 403
    assert blocked_req.json()["error"]["code"] == "MEMBER_SUSPENDED"


@pytest.mark.asyncio
async def test_owner_protection_and_transfer(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # Invite colleague
    inv = await client.post(
        "/api/v1/organization/invitations",
        json={"email": "successor@example.com", "role": "admin"},
        headers=headers,
    )
    token = inv.json()["data"]["invitation_token"]

    acc = await client.post(
        "/api/v1/organization/invitations/accept",
        json={"token": token, "name": "Successor", "password": "Password123"},
    )
    successor_user_id = acc.json()["data"]["user"]["id"]

    # Find current owner member ID
    members_res = await client.get("/api/v1/organization/members", headers=headers)
    members = members_res.json()["data"]["items"]
    owner_member = next(m for m in members if m["role"] == "owner")

    # 1. Removing the owner must be rejected
    del_owner = await client.delete(f"/api/v1/organization/members/{owner_member['id']}", headers=headers)
    assert del_owner.status_code == 403
    assert del_owner.json()["error"]["code"] == "CANNOT_REMOVE_OWNER"

    # 2. Transfer ownership to successor
    transfer_res = await client.post(
        "/api/v1/organization/transfer-ownership",
        json={"new_owner_user_id": successor_user_id},
        headers=headers,
    )
    assert transfer_res.status_code == 200
    assert transfer_res.json()["data"]["transferred"] is True


@pytest.mark.asyncio
async def test_teams_system(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Create team
    create_res = await client.post(
        "/api/v1/teams",
        json={"name": "Engineering Team", "description": "Handles dev tasks"},
        headers=headers,
    )
    assert create_res.status_code == 201
    team_id = create_res.json()["data"]["id"]

    # 2. Add member to team
    user_id = registered_user["user"]["id"]
    add_res = await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": user_id, "role": "lead"},
        headers=headers,
    )
    assert add_res.status_code == 201
    assert add_res.json()["data"]["role"] == "lead"

    # 3. List team members
    list_res = await client.get(f"/api/v1/teams/{team_id}/members", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 1

    # 4. Remove member from team
    rem_res = await client.delete(f"/api/v1/teams/{team_id}/members/{user_id}", headers=headers)
    assert rem_res.status_code == 200
    assert rem_res.json()["data"]["removed"] is True

    # 5. Delete team
    del_res = await client.delete(f"/api/v1/teams/{team_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True
