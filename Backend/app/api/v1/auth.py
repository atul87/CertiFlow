from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, status
from app.api.deps import (
    get_current_user_and_org,
    get_client_ip,
    get_client_user_agent
)
from app.schemas.common import APIResponse
from app.schemas.auth import (
    TokenResponse,
    RefreshTokenRequest,
    AuthMeResponse
)
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user with default organization"
)
async def register(
    data: UserRegisterRequest,
    request: Request
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    token_response = await AuthService.register(data, ip_address=ip, user_agent=ua)
    return APIResponse.ok(token_response)


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="User login with email and password"
)
async def login(
    data: UserLoginRequest,
    request: Request
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    token_response = await AuthService.login(data, ip_address=ip, user_agent=ua)
    return APIResponse.ok(token_response)


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and issue new access token"
)
async def refresh_tokens(
    data: RefreshTokenRequest
):
    token_response = await AuthService.refresh(data.refresh_token)
    return APIResponse.ok(token_response)


@router.post(
    "/logout",
    response_model=APIResponse[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Revoke session and refresh token"
)
async def logout(
    request: Request,
    data: Optional[RefreshTokenRequest] = None,
    context: Optional[Dict[str, Any]] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    user_id = context.get("user_id") if context else None
    token = data.refresh_token if data else None

    await AuthService.logout(raw_refresh_token=token, user_id=user_id, ip_address=ip, user_agent=ua)
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
