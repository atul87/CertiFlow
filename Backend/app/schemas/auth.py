from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse
from app.schemas.organization import OrganizationResponse


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    organization: OrganizationResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token received during login/register")


class AuthMeResponse(BaseModel):
    user: UserResponse
    organization: OrganizationResponse
    role: str
