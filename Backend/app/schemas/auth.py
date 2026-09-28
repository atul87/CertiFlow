from typing import Optional
from pydantic import BaseModel, EmailStr, Field
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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered user email address")


class ForgotPasswordResponse(BaseModel):
    message: str = "If this email is registered, password reset instructions have been sent."
    # For testing / developer convenience in local dev:
    reset_token: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=16, description="Single-use password reset token")
    new_password: str = Field(..., min_length=8, description="New strong password (min 8 characters)")


class ResetPasswordResponse(BaseModel):
    message: str = "Password has been successfully reset. Please log in with your new password."


class ReauthRequest(BaseModel):
    password: str = Field(..., min_length=1, description="Current user password for confirmation")
