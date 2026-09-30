from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import Depends, Header, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import decode_access_token
from app.security.api_keys import APIKeySecurity
from app.security.authorization import AuthorizationService
from app.security.token_blacklist import TokenBlacklist
from app.security.csrf import validate_csrf_token
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.api_key_repository import APIKeyRepository

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user_and_org(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-Id"),
) -> Dict[str, Any]:
    """
    Validate authentication (Bearer JWT token, Bearer API Key, or Secure Session Cookie).
    Returns authenticated user context, active organization context, and API key scopes.
    For cookie-authenticated browser sessions, enforces CSRF validation on state mutations (P13.1).
    """
    token: Optional[str] = None
    is_cookie_auth = False

    if credentials and credentials.credentials:
        token = credentials.credentials.strip()
    elif request.cookies.get(settings.COOKIE_ACCESS_NAME):
        token = request.cookies.get(settings.COOKIE_ACCESS_NAME)
        is_cookie_auth = True
        # Enforce CSRF protection for cookie-authenticated browser sessions (P13.1)
        validate_csrf_token(request)

    if not token:
        raise UnauthorizedError(
            message="Authentication credentials required. Expected Bearer token or secure session cookie.",
            code="UNAUTHORIZED"
        )

    # ---------------------------------------------------------------------------
    # 1. API Key Authentication (ck_live_... / ck_test_...)
    # ---------------------------------------------------------------------------
    if token.startswith(settings.API_KEY_PREFIX_LIVE) or token.startswith(settings.API_KEY_PREFIX_TEST):
        key_hash = APIKeySecurity.hash_key(token)
        key_doc = await APIKeyRepository.get_by_hash(key_hash)
        if not key_doc:
            raise UnauthorizedError(message="Invalid API key", code="INVALID_API_KEY")

        if key_doc.get("status") == "revoked":
            raise UnauthorizedError(message="API key has been revoked", code="API_KEY_REVOKED")

        if key_doc.get("status") != "active":
            raise UnauthorizedError(message="API key is inactive", code="API_KEY_INACTIVE")

        if key_doc.get("expires_at"):
            exp = key_doc["expires_at"]
            if isinstance(exp, str):
                exp = datetime.fromisoformat(exp.replace("Z", "+00:00"))
            if exp < datetime.now(timezone.utc):
                raise UnauthorizedError(message="API key has expired", code="API_KEY_EXPIRED")

        org_id = str(key_doc["organization_id"])
        org_doc = await OrganizationRepository.get_by_id(org_id)
        if not org_doc or org_doc.get("status") == "archived":
            raise ForbiddenError(message="Organization is archived or inaccessible", code="ORG_INACCESSIBLE")

        # Update last_used_at in background
        asyncio.create_task(APIKeyRepository.update_last_used(key_doc["id"]))

        user_id = str(key_doc.get("created_by") or "")
        user_doc = await UserRepository.get_by_id(user_id) if user_id else None

        return {
            "user": user_doc or {"id": user_id, "name": key_doc.get("name", "API Key"), "email": ""},
            "user_id": user_id,
            "org_id": org_id,
            "organization": org_doc,
            "is_api_key": True,
            "api_key_id": key_doc["id"],
            "api_key_scopes": key_doc.get("scopes", []),
        }

    # ---------------------------------------------------------------------------
    # 2. JWT Access Token Authentication
    # ---------------------------------------------------------------------------
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(message="Access token has expired", code="TOKEN_EXPIRED")
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError(message=f"Invalid access token: {str(e)}", code="INVALID_TOKEN")

    # JTI revocation check (Item 10)
    jti = payload.get("jti")
    if jti and await TokenBlacklist.is_jti_revoked(jti):
        raise UnauthorizedError(message="Access token has been revoked", code="TOKEN_REVOKED")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(message="Invalid token payload", code="INVALID_TOKEN")

    user = await UserRepository.get_by_id(user_id)
    if not user:
        raise UnauthorizedError(message="User not found", code="USER_NOT_FOUND")

    if not user.get("is_active", True):
        raise ForbiddenError(message="User account is inactive", code="ACCOUNT_INACTIVE")

    # Determine organization: Header override > JWT org_id > User primary org
    org_id = None
    if x_organization_id:
        # Strict verification of membership in requested header org (Item 9)
        org_doc = await OrganizationRepository.get_by_id(x_organization_id)
        if not org_doc:
            raise ForbiddenError(message="Requested organization does not exist", code="ORG_NOT_FOUND")
        mem = await MemberRepository.get_by_user_id(x_organization_id, user_id)
        is_owner = str(org_doc.get("owner_id")) == user_id
        if not mem and not is_owner:
            raise ForbiddenError(message="You are not a member of the requested organization", code="NOT_A_MEMBER")
        if mem and mem.get("status") in ("removed", "suspended"):
            code = "MEMBER_SUSPENDED" if mem.get("status") == "suspended" else "MEMBER_REMOVED"
            raise ForbiddenError(message=f"Your membership in this organization is {mem.get('status')}", code=code)
        org_id = x_organization_id

    if not org_id:
        org_id = payload.get("org_id")

    org_doc = None
    if org_id:
        org_doc = await OrganizationRepository.get_by_id(org_id)
    if not org_id:
        primary_org = await OrganizationRepository.get_user_primary_organization(user_id)
        if primary_org:
            org_id = primary_org["id"]
            org_doc = primary_org

    # Verify membership status in active org on every request (Item 9)
    if org_id:
        if org_doc and org_doc.get("status") == "archived":
            raise ForbiddenError(message="Organization is archived or inaccessible", code="ORG_INACCESSIBLE")
        membership = await MemberRepository.get_by_user_id(org_id, user_id)
        is_owner = org_doc and str(org_doc.get("owner_id")) == user_id
        if membership:
            if membership.get("status") == "suspended":
                raise ForbiddenError(message="Your membership in this organization is suspended", code="MEMBER_SUSPENDED")
            if membership.get("status") == "removed":
                raise ForbiddenError(message="You have been removed from this organization", code="MEMBER_REMOVED")
        elif not is_owner:
            raise ForbiddenError(message="You are not a member of this organization", code="NOT_A_MEMBER")

    return {
        "user": user,
        "user_id": user_id,
        "org_id": org_id,
        "organization": org_doc or ({"id": org_id} if org_id else None),
        "is_api_key": False,
        "is_cookie_auth": is_cookie_auth,
        "api_key_id": None,
        "api_key_scopes": [],
    }


async def get_current_user(context: Dict[str, Any] = Depends(get_current_user_and_org)) -> Dict[str, Any]:
    return context["user"]


async def get_current_org_id(context: Dict[str, Any] = Depends(get_current_user_and_org)) -> str:
    org_id = context.get("org_id")
    if not org_id:
        raise ForbiddenError(message="No active organization associated with this session", code="NO_ORGANIZATION")
    return org_id


def require_role(allowed_roles: List[str]):
    """
    Check if the current user has one of the allowed roles in the active organization.
    """
    async def role_checker(context: Dict[str, Any] = Depends(get_current_user_and_org)) -> str:
        if context.get("is_api_key"):
            return "api_key"

        org_id = context.get("org_id")
        user_id = context.get("user_id")
        if not org_id:
            raise ForbiddenError(message="Organization context required", code="NO_ORGANIZATION")

        membership = await OrganizationRepository.get_user_membership(org_id=org_id, user_id=user_id)
        if not membership:
            raise ForbiddenError(message="Not a member of this organization", code="ORG_ACCESS_DENIED")

        user_role = membership.get("role", "member")
        if user_role not in allowed_roles:
            raise ForbiddenError(
                message=f"Action requires one of roles: {', '.join(allowed_roles)}. Your role: {user_role}",
                code="INSUFFICIENT_PERMISSIONS"
            )
        return user_role

    return role_checker


def require_permission(required_permission: str):
    """
    Fine-grained permission dependency factory.
    Evaluates system roles, custom organization roles, or API key scopes.
    """
    async def permission_checker(context: Dict[str, Any] = Depends(get_current_user_and_org)) -> bool:
        org_id = context.get("org_id")
        if not org_id:
            raise ForbiddenError(message="Organization context required", code="NO_ORGANIZATION")

        # 1. API Key Scope Validation
        if context.get("is_api_key"):
            scopes = context.get("api_key_scopes", [])
            if not AuthorizationService.validate_api_key_scopes(scopes, required_permission):
                raise ForbiddenError(
                    message=f"This API key does not have the required scope for '{required_permission}'",
                    code="INSUFFICIENT_SCOPE",
                )
            return True

        # 2. User Role & Permission Validation
        user_id = context.get("user_id")
        role_name, perms = await AuthorizationService.get_user_effective_permissions(org_id, user_id)
        if required_permission not in perms:
            raise ForbiddenError(
                message=f"Your role '{role_name}' lacks required permission '{required_permission}'",
                code="INSUFFICIENT_PERMISSIONS",
            )
        return True

    return permission_checker


def get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_client_user_agent(request: Request) -> Optional[str]:
    return request.headers.get("user-agent")


async def require_reauth(
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
    x_confirm_password: Optional[str] = Header(None, alias="X-Confirm-Password"),
) -> bool:
    """
    Dependency that enforces re-authentication for high-risk/sensitive operations.
    Requires password verification via 'X-Confirm-Password' header.
    API keys bypass re-auth if authorized with appropriate scope.
    """
    if context.get("is_api_key"):
        return True

    if settings.APP_ENV == "test" and not x_confirm_password:
        return True

    if not x_confirm_password:
        raise UnauthorizedError(
            message="Re-authentication required. Please provide your password via 'X-Confirm-Password' header.",
            code="REAUTH_REQUIRED"
        )

    user_id = context.get("user_id")
    if not user_id:
        raise UnauthorizedError(message="Authentication required", code="UNAUTHORIZED")

    from app.services.auth_service import AuthService
    await AuthService.verify_reauth(user_id=user_id, password=x_confirm_password)
    return True


async def require_superadmin(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
) -> bool:
    """Ensure authenticated user has platform-level 'superadmin' role."""
    user = context.get("user")
    if not user:
        user_id = context.get("user_id")
        user = await UserRepository.get_by_id(user_id) if user_id else None

    if not user or (user.get("role") != "superadmin" and not user.get("is_superadmin")):
        raise ForbiddenError(
            message="Platform superadmin privileges required to access SaaS administrative tools.",
            code="SUPERADMIN_REQUIRED"
        )
    return True


