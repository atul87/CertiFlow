from typing import Optional, List, Dict, Any
from fastapi import Depends, Header, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user_and_org(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    Validate JWT access token and return context dict containing user and current org_id.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedError(
            message="Missing or malformed Authorization header. Expected 'Bearer <token>'",
            code="UNAUTHORIZED"
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(message="Access token has expired", code="TOKEN_EXPIRED")
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError(message=f"Invalid access token: {str(e)}", code="INVALID_TOKEN")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(message="Invalid token payload", code="INVALID_TOKEN")

    user = await UserRepository.get_by_id(user_id)
    if not user:
        raise UnauthorizedError(message="User not found", code="USER_NOT_FOUND")

    if not user.get("is_active", True):
        raise ForbiddenError(message="User account is inactive", code="ACCOUNT_INACTIVE")

    org_id = payload.get("org_id")
    if not org_id:
        # Fallback to primary organization
        primary_org = await OrganizationRepository.get_user_primary_organization(user_id)
        if primary_org:
            org_id = primary_org["id"]

    return {
        "user": user,
        "user_id": user_id,
        "org_id": org_id
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
    Dependency factory to check if the current user has one of the allowed roles in the active organization.
    """
    async def role_checker(context: Dict[str, Any] = Depends(get_current_user_and_org)) -> str:
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


def get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_client_user_agent(request: Request) -> Optional[str]:
    return request.headers.get("user-agent")
