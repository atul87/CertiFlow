import logging
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError, NotFoundError, ForbiddenError
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_token
)
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse
from app.schemas.organization import OrganizationResponse
from app.schemas.auth import TokenResponse, AuthMeResponse

logger = logging.getLogger(__name__)


class AuthService:
    @classmethod
    async def register(
        cls,
        data: UserRegisterRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        # 1. Check if email already registered
        existing_user = await UserRepository.get_by_email(data.email)
        if existing_user:
            raise ConflictError(message="A user with this email address already exists", code="DUPLICATE_EMAIL")

        # 2. Hash password with Argon2id
        pw_hash = hash_password(data.password)

        # 3. Create user document
        user = await UserRepository.create(
            email=data.email,
            password_hash=pw_hash,
            name=data.name
        )

        # 4. Automatically create organization for user
        org_name = f"{data.name}'s Organization"
        org = await OrganizationRepository.create(
            name=org_name,
            owner_id=user["id"]
        )

        # 5. Issue JWT access token + refresh token
        access_token = create_access_token(user_id=user["id"], org_id=org["id"])
        raw_refresh, token_hash, expires_at = generate_refresh_token(user_id=user["id"], org_id=org["id"])

        # 6. Save hashed refresh token
        await RefreshTokenRepository.create(
            user_id=user["id"],
            organization_id=org["id"],
            token_hash=token_hash,
            expires_at=expires_at
        )

        # 7. Audit log registration & organization creation
        await AuditLogRepository.log_event(
            action="user.registered",
            resource_type="user",
            resource_id=user["id"],
            organization_id=org["id"],
            user_id=user["id"],
            metadata={"email": user["email"]},
            ip_address=ip_address,
            user_agent=user_agent
        )

        await AuditLogRepository.log_event(
            action="organization.created",
            resource_type="organization",
            resource_id=org["id"],
            organization_id=org["id"],
            user_id=user["id"],
            metadata={"name": org["name"], "slug": org["slug"]},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user),
            organization=OrganizationResponse(**org)
        )

    @classmethod
    async def login(
        cls,
        data: UserLoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        user = await UserRepository.get_by_email(data.email)
        if not user:
            raise UnauthorizedError(message="Invalid email or password", code="INVALID_CREDENTIALS")

        if not user.get("is_active", True):
            raise ForbiddenError(message="Account has been deactivated", code="ACCOUNT_INACTIVE")

        # Verify Argon2 password
        if not verify_password(data.password, user.get("password_hash", "")):
            raise UnauthorizedError(message="Invalid email or password", code="INVALID_CREDENTIALS")

        # Retrieve user's primary organization
        org = await OrganizationRepository.get_user_primary_organization(user["id"])
        org_id = org["id"] if org else None

        # Issue access token & refresh token
        access_token = create_access_token(user_id=user["id"], org_id=org_id)
        raw_refresh, token_hash, expires_at = generate_refresh_token(user_id=user["id"], org_id=org_id)

        await RefreshTokenRepository.create(
            user_id=user["id"],
            organization_id=org_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        # Audit log login
        await AuditLogRepository.log_event(
            action="user.login",
            resource_type="user",
            resource_id=user["id"],
            organization_id=org_id,
            user_id=user["id"],
            metadata={"email": user["email"]},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user),
            organization=OrganizationResponse(**org) if org else OrganizationResponse(
                id="default", name="Default", slug="default", owner_id=user["id"],
                created_at=user["created_at"], updated_at=user["updated_at"]
            )
        )

    @classmethod
    async def refresh(cls, raw_refresh_token: str) -> TokenResponse:
        token_hash = hash_token(raw_refresh_token)
        record = await RefreshTokenRepository.find_valid(token_hash)
        if not record:
            raise UnauthorizedError(message="Invalid or expired refresh token", code="INVALID_REFRESH_TOKEN")

        # Revoke old refresh token (rotation for security)
        await RefreshTokenRepository.revoke(token_hash)

        user = await UserRepository.get_by_id(record["user_id"])
        if not user or not user.get("is_active", True):
            raise UnauthorizedError(message="User not found or inactive", code="USER_INACTIVE")

        org_id = record.get("organization_id")
        org = None
        if org_id:
            org = await OrganizationRepository.get_by_id(org_id)
        if not org:
            org = await OrganizationRepository.get_user_primary_organization(user["id"])

        org_id_val = org["id"] if org else None

        # Issue new tokens
        access_token = create_access_token(user_id=user["id"], org_id=org_id_val)
        new_raw_refresh, new_token_hash, expires_at = generate_refresh_token(
            user_id=user["id"],
            org_id=org_id_val
        )

        await RefreshTokenRepository.create(
            user_id=user["id"],
            organization_id=org_id_val,
            token_hash=new_token_hash,
            expires_at=expires_at
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_raw_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user),
            organization=OrganizationResponse(**org) if org else OrganizationResponse(
                id="default", name="Default", slug="default", owner_id=user["id"],
                created_at=user["created_at"], updated_at=user["updated_at"]
            )
        )

    @classmethod
    async def logout(
        cls,
        raw_refresh_token: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        if raw_refresh_token:
            token_hash = hash_token(raw_refresh_token)
            await RefreshTokenRepository.revoke(token_hash)
        elif user_id:
            await RefreshTokenRepository.revoke_all_for_user(user_id)

        if user_id:
            await AuditLogRepository.log_event(
                action="user.logout",
                resource_type="user",
                resource_id=user_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
        return True

    @classmethod
    async def get_current_user_profile(cls, user_id: str, org_id: Optional[str] = None) -> AuthMeResponse:
        user = await UserRepository.get_by_id(user_id)
        if not user:
            raise NotFoundError(message="User not found", code="USER_NOT_FOUND")

        org = None
        role = "member"
        if org_id:
            org = await OrganizationRepository.get_by_id(org_id)
            membership = await OrganizationRepository.get_user_membership(org_id, user_id)
            if membership:
                role = membership.get("role", "member")

        if not org:
            org = await OrganizationRepository.get_user_primary_organization(user_id)
            if org:
                role = org.get("member_role", "member")

        if not org:
            raise NotFoundError(message="User has no assigned organization", code="ORGANIZATION_NOT_FOUND")

        return AuthMeResponse(
            user=UserResponse(**user),
            organization=OrganizationResponse(**org),
            role=role
        )
