"""
Central Permission Registry and System Role Definitions (P8).
Enforces fine-grained Role-Based Access Control (RBAC) across the platform.
"""
from __future__ import annotations
from typing import Set, Dict, List

# ---------------------------------------------------------------------------
# All registered system permissions
# ---------------------------------------------------------------------------
PERMISSIONS: Set[str] = {
    # Organization
    "organization.read",
    "organization.update",
    "organization.transfer_ownership",

    # Members & Invitations
    "members.read",
    "members.invite",
    "members.update",
    "members.remove",

    # Roles
    "roles.read",
    "roles.manage",

    # Teams
    "teams.read",
    "teams.manage",

    # Templates & Assets
    "templates.read",
    "templates.create",
    "templates.update",
    "templates.delete",

    # CSV/Excel Imports
    "imports.read",
    "imports.create",

    # Certificates
    "certificates.read",
    "certificates.create",
    "certificates.revoke",
    "certificates.restore",

    # Issuance Jobs
    "issuance.read",
    "issuance.create",
    "issuance.manage",

    # Emails & Notifications
    "emails.read",
    "emails.send",

    # Analytics & Usage
    "analytics.read",
    "api_usage.read",

    # Reports
    "reports.read",
    "reports.create",
    "reports.download",

    # API Keys & Service Accounts
    "api_keys.read",
    "api_keys.create",
    "api_keys.revoke",
    "api_keys.manage",
    "service_accounts.read",
    "service_accounts.manage",

    # Webhooks
    "webhooks.read",
    "webhooks.create",
    "webhooks.update",
    "webhooks.delete",
    "webhooks.manage",
}

# ---------------------------------------------------------------------------
# Default system role permission mappings
# ---------------------------------------------------------------------------
SYSTEM_ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "owner": set(PERMISSIONS),  # full unconstrained authority
    "admin": {p for p in PERMISSIONS if p != "organization.transfer_ownership"},
    "member": {
        "organization.read",
        "members.read",
        "teams.read",
        "templates.read",
        "imports.read",
        "imports.create",
        "certificates.read",
        "certificates.create",
        "issuance.read",
        "issuance.create",
        "emails.read",
        "emails.send",
        "analytics.read",
        "reports.read",
        "reports.create",
        "reports.download",
    },
    "viewer": {
        "organization.read",
        "members.read",
        "teams.read",
        "templates.read",
        "certificates.read",
        "issuance.read",
        "emails.read",
        "analytics.read",
        "reports.read",
    },
}

# ---------------------------------------------------------------------------
# Scope-to-permission mapping for API keys
# ---------------------------------------------------------------------------
API_SCOPE_PERMISSIONS: Dict[str, Set[str]] = {
    "certificates:read": {"certificates.read"},
    "certificates:create": {"certificates.create"},
    "certificates:revoke": {"certificates.revoke"},
    "certificates:restore": {"certificates.restore"},
    "templates:read": {"templates.read"},
    "templates:manage": {"templates.create", "templates.update", "templates.delete"},
    "imports:read": {"imports.read"},
    "imports:create": {"imports.create"},
    "issuance:read": {"issuance.read"},
    "issuance:create": {"issuance.create"},
    "issuance:manage": {"issuance.manage"},
    "email:send": {"emails.send"},
    "email:read": {"emails.read"},
    "verification:read": {"certificates.read"},
    "reports:read": {"reports.read", "reports.download"},
    "reports:create": {"reports.create"},
    "webhooks:read": {"webhooks.read"},
    "webhooks:manage": {"webhooks.manage"},
}


def get_role_permissions(role_name: str, custom_permissions: List[str] | None = None) -> Set[str]:
    """Retrieve effective permissions for a system or custom role."""
    if role_name in SYSTEM_ROLE_PERMISSIONS:
        return SYSTEM_ROLE_PERMISSIONS[role_name]
    if custom_permissions:
        return set(custom_permissions) & PERMISSIONS
    return set()
