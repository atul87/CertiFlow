from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, Response, status
from app.api.deps import (
    get_current_user_and_org,
    get_client_ip,
    get_client_user_agent
)
from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.schemas.common import APIResponse
from app.security.csrf import generate_csrf_token
from app.schemas.auth import (
    TokenResponse,
    RefreshTokenRequest,
    AuthMeResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse
)
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> str:
    """
    Set hardened session cookies:
    1. certiflow_access_token: HttpOnly, Secure (in non-dev), SameSite=Lax, Path=/
    2. certiflow_refresh_token: HttpOnly, Secure, SameSite=Lax, Path=/api/v1/auth
    3. certiflow_csrf_token: Accessible to client JS for Double Submit CSRF defense, Path=/
    Returns the generated CSRF token.
    """
    secure_cookie = settings.APP_ENV not in ("development", "test")
    csrf_token = generate_csrf_token()

    # 1. HttpOnly Access Token Cookie
    response.set_cookie(
        key=settings.COOKIE_ACCESS_NAME,
        value=access_token,
        httponly=True,
        secure=secure_cookie,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )

    # 2. HttpOnly Refresh Token Cookie
    response.set_cookie(
        key=settings.COOKIE_REFRESH_NAME,
        value=refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
        domain=settings.COOKIE_DOMAIN,
    )

    # 3. Client-readable CSRF Cookie (for X-CSRF-Token header in mutating requests)
    response.set_cookie(
        key=settings.COOKIE_CSRF_NAME,
        value=csrf_token,
        httponly=False,
        secure=secure_cookie,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )

    return csrf_token


def _clear_auth_cookies(response: Response) -> None:
    """Clear all session and CSRF cookies on logout."""
    response.delete_cookie(key=settings.COOKIE_ACCESS_NAME, path="/", domain=settings.COOKIE_DOMAIN)
    response.delete_cookie(key=settings.COOKIE_REFRESH_NAME, path="/api/v1/auth", domain=settings.COOKIE_DOMAIN)
    response.delete_cookie(key=settings.COOKIE_CSRF_NAME, path="/", domain=settings.COOKIE_DOMAIN)


@router.post(
    "/register",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user with default organization"
)
async def register(
    data: UserRegisterRequest,
    request: Request,
    response: Response,
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    token_response = await AuthService.register(data, ip_address=ip, user_agent=ua)
    _set_auth_cookies(response, token_response.access_token, token_response.refresh_token)
    return APIResponse.ok(token_response)


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="User login with email and password"
)
async def login(
    data: UserLoginRequest,
    request: Request,
    response: Response,
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    token_response = await AuthService.login(data, ip_address=ip, user_agent=ua)
    _set_auth_cookies(response, token_response.access_token, token_response.refresh_token)
    return APIResponse.ok(token_response)


@router.post(
    "/demo-session",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Server-controlled demo session (development/staging only — P13.1)"
)
async def create_demo_session(
    request: Request,
    response: Response,
):
    """
    Server-controlled demo session endpoint.
    Strictly forbidden in production environments.
    Issues cryptographically valid tokens and HttpOnly session cookies for the demo tenant.
    """
    env = (settings.APP_ENV or "").lower().strip()
    if env in ("production", "prod") or not settings.ALLOW_DEMO_AUTH:
        raise ForbiddenError(
            message="Demo authentication is disabled in production environments.",
            code="DEMO_AUTH_DISABLED"
        )

    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    token_response = await AuthService.create_or_get_demo_session(ip_address=ip, user_agent=ua)
    _set_auth_cookies(response, token_response.access_token, token_response.refresh_token)
    return APIResponse.ok(token_response)


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and issue new access token"
)
async def refresh_tokens(
    request: Request,
    response: Response,
    data: Optional[RefreshTokenRequest] = None,
):
    token = (data.refresh_token if data else None) or request.cookies.get(settings.COOKIE_REFRESH_NAME)
    if not token:
        raise UnauthorizedError(message="Refresh token missing from body and cookies", code="REFRESH_TOKEN_REQUIRED")
    token_response = await AuthService.refresh(token)
    _set_auth_cookies(response, token_response.access_token, token_response.refresh_token)
    return APIResponse.ok(token_response)


@router.post(
    "/logout",
    response_model=APIResponse[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Revoke session and refresh token"
)
async def logout(
    request: Request,
    response: Response,
    data: Optional[RefreshTokenRequest] = None,
    context: Optional[Dict[str, Any]] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    user_id = context.get("user_id") if context else None
    token = (data.refresh_token if data else None) or request.cookies.get(settings.COOKIE_REFRESH_NAME)

    # Extract access token from Bearer header or HttpOnly cookie for JTI revocation — P12.10 / P13.1
    raw_access_token = None
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        raw_access_token = auth_header[7:].strip()
    elif request.cookies.get(settings.COOKIE_ACCESS_NAME):
        raw_access_token = request.cookies.get(settings.COOKIE_ACCESS_NAME)

    await AuthService.logout(
        raw_refresh_token=token,
        user_id=user_id,
        raw_access_token=raw_access_token,
        ip_address=ip,
        user_agent=ua
    )
    _clear_auth_cookies(response)
    return APIResponse.ok({"message": "Successfully logged out"})


@router.get(
    "/me",
    response_model=APIResponse[AuthMeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user profile and active organization"
)
async def get_current_profile(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    profile = await AuthService.get_current_user_profile(
        user_id=context["user_id"],
        org_id=context.get("org_id")
    )
    return APIResponse.ok(profile)


@router.post(
    "/forgot-password",
    response_model=APIResponse[ForgotPasswordResponse],
    status_code=status.HTTP_200_OK,
    summary="Request password reset token (account enumeration protected)"
)
async def forgot_password(
    data: ForgotPasswordRequest,
    request: Request
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    result = await AuthService.forgot_password(data.email, ip_address=ip, user_agent=ua)
    return APIResponse.ok(result)


@router.post(
    "/reset-password",
    response_model=APIResponse[ResetPasswordResponse],
    status_code=status.HTTP_200_OK,
    summary="Reset password using single-use reset token"
)
async def reset_password(
    data: ResetPasswordRequest,
    request: Request
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    result = await AuthService.reset_password(
        token=data.token,
        new_password=data.new_password,
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(result)

