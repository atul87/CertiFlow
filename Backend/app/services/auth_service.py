import logging
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    UnauthorizedError,
    NotFoundError,
    ForbiddenError,
    ValidationError,
    RateLimitError
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    generate_password_reset_token,
    hash_token
)
from app.core.database import DatabaseManager
from app.security.token_blacklist import TokenBlacklist
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.security.rate_limiter import APIRateLimiter
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse
from app.schemas.organization import OrganizationResponse
from app.schemas.auth import (
    TokenResponse,
    AuthMeResponse,
    ForgotPasswordResponse,
    ResetPasswordResponse
)

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

        # 3. Create user document, organization, subscription, and refresh token within transaction boundary
        async with DatabaseManager.transaction_scope():
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

            # Initialize default SaaS subscription (Starter trial)
            from app.services.subscription_service import SubscriptionService
            await SubscriptionService.initialize_org_subscription(org["id"], trial=True)

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
        # 1. Login rate limit check
        rate_key = f"login:{ip_address or 'unknown'}:{data.email.lower().strip()}"
        allowed, _, _, retry_after = await APIRateLimiter.check_rate_limit(
            identifier=rate_key,
            limit_per_minute=settings.LOGIN_RATE_LIMIT_PER_MINUTE
        )
        if not allowed:
            raise RateLimitError(
                message="Too many login attempts. Please try again later.",
                code="LOGIN_RATE_LIMIT_EXCEEDED",
                retry_after=retry_after or 60
            )

        user = await UserRepository.get_by_email(data.email)
        if not user or not verify_password(data.password, user.get("password_hash", "")):
            # Audit log failed attempt without revealing whether email exists
            await AuditLogRepository.log_event(
                action="user.login_failed",
                resource_type="user",
                resource_id=user["id"] if user else "unknown",
                user_id=user["id"] if user else None,
                metadata={"email": data.email},
                ip_address=ip_address,
                user_agent=user_agent
            )
            raise UnauthorizedError(message="Invalid email or password", code="INVALID_CREDENTIALS")

        if not user.get("is_active", True):
            raise ForbiddenError(message="Account has been deactivated", code="ACCOUNT_INACTIVE")

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
        raw_access_token: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        import time
        if raw_access_token:
            try:
                payload = decode_access_token(raw_access_token)
                jti = payload.get("jti")
                exp = payload.get("exp", 0)
                now = int(time.time())
                ttl = max(1, exp - now)
                if jti:
                    await TokenBlacklist.revoke_jti(jti, ttl_seconds=ttl)
            except Exception as exc:
                logger.debug("Could not decode access token during logout: %s", exc)

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

    @classmethod
    async def forgot_password(
        cls,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ForgotPasswordResponse:
        """
        Request a password reset. Never reveals whether the email exists
        in the database to prevent account enumeration.
        """
        clean_email = email.lower().strip()
        user = await UserRepository.get_by_email(clean_email)
        raw_token = None

        if user and user.get("is_active", True):
            # Invalidate any existing unused reset tokens for this user
            await PasswordResetRepository.invalidate_all_for_user(user["id"])

            # Generate high-entropy single-use token (32 bytes urlsafe)
            raw_token, token_hash, expires_at = generate_password_reset_token()

            # Store hashed token in database
            await PasswordResetRepository.create_token(
                user_id=user["id"],
                token_hash=token_hash,
                expires_at=expires_at,
                ip_address=ip_address
            )

            # Audit log
            await AuditLogRepository.log_event(
                action="password.reset_requested",
                resource_type="user",
                resource_id=user["id"],
                user_id=user["id"],
                metadata={"email": clean_email},
                ip_address=ip_address,
                user_agent=user_agent
            )

        # In dev/test environments, expose token in response for testing convenience
        reset_token_response = raw_token if (settings.APP_ENV in ("development", "test") and raw_token) else None

        return ForgotPasswordResponse(
            message="If this email is registered, password reset instructions have been sent.",
            reset_token=reset_token_response
        )

    @classmethod
    async def reset_password(
        cls,
        token: str,
        new_password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ResetPasswordResponse:
        """
        Reset password using a high-entropy single-use token.
        Validates token hash, updates password hash, marks token used,
        and revokes all active refresh tokens for the user.
        """
        token_hash = hash_token(token)
        token_record = await PasswordResetRepository.find_valid_token(token_hash)
        if not token_record:
            raise ValidationError(
                message="Invalid, expired, or already used password reset token",
                code="INVALID_RESET_TOKEN"
            )

        user_id = token_record["user_id"]
        user = await UserRepository.get_by_id(user_id)
        if not user or not user.get("is_active", True):
            raise ValidationError(
                message="User account is inactive or not found",
                code="USER_INACTIVE"
            )

        # Hash new password with Argon2id
        new_pw_hash = hash_password(new_password)
        await UserRepository.update(user_id, {"password_hash": new_pw_hash})

        # Mark token as used
        await PasswordResetRepository.mark_used(token_hash)

        # Revoke all existing sessions/refresh tokens for this user
        await RefreshTokenRepository.revoke_all_for_user(user_id)

        # Audit log
        await AuditLogRepository.log_event(
            action="password.reset_completed",
            resource_type="user",
            resource_id=user_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return ResetPasswordResponse(
            message="Password has been successfully reset. Please log in with your new password."
        )

    @classmethod
    async def verify_reauth(cls, user_id: str, password: str) -> bool:
        """Verify user's password for sensitive/high-risk operations."""
        user = await UserRepository.get_by_id(user_id)
        if not user or not verify_password(password, user.get("password_hash", "")):
            raise UnauthorizedError(
                message="Invalid password confirmation for high-risk action",
                code="REAUTH_REQUIRED"
            )
        return True

    @classmethod
    async def create_or_get_demo_session(
        cls,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        """
        Create or get demo user session (development/staging only — P13.1).
        Ensures a demo organization, default subscription, and valid cryptographic tokens exist.
        """
        demo_email = "demo@certiflow.io"
        user = await UserRepository.get_by_email(demo_email)

        if not user:
            pw_hash = hash_password("DemoSecurePass2026!")
            async with DatabaseManager.transaction_scope():
                user = await UserRepository.create(
                    email=demo_email,
                    password_hash=pw_hash,
                    name="Demo Administrator"
                )
                org = await OrganizationRepository.create(
                    name="Demo Workspace",
                    owner_id=user["id"]
                )
                from app.services.subscription_service import SubscriptionService
                await SubscriptionService.initialize_org_subscription(org["id"], trial=True)
        else:
            org = await OrganizationRepository.get_user_primary_organization(user["id"])
            if not org:
                org = await OrganizationRepository.create(
                    name="Demo Workspace",
                    owner_id=user["id"]
                )

        access_token = create_access_token(user_id=user["id"], org_id=org["id"])
        raw_refresh, token_hash, expires_at = generate_refresh_token(user_id=user["id"], org_id=org["id"])

        await RefreshTokenRepository.create(
            user_id=user["id"],
            organization_id=org["id"],
            token_hash=token_hash,
            expires_at=expires_at
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user),
            organization=OrganizationResponse(**org) if org else OrganizationResponse(
                id=org["id"], name=org.get("name", "Demo Workspace"), slug=org.get("slug", "demo"), owner_id=user["id"],
                created_at=user["created_at"], updated_at=user["updated_at"]
            )
        )


