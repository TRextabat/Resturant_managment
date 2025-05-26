from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class RegisterResponse(BaseModel):
    id: UUID
    message: str
    verifection_token: str
    token_type: str



class VerifyEmailResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="User's refresh token")

class UserProfileResponse(BaseModel):
    id: UUID
    primary_email: EmailStr = Field(..., description="Primary email of the user")
    primary_email_verified: bool = Field(..., description="Indicates if primary email is verified")

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token for API authentication")
    refresh_token: Optional[str] = Field(None, description="Refresh token for obtaining new access tokens")
    token_type: str = "bearer"