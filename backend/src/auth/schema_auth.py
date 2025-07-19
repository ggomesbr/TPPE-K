"""
Hospital Management System - Authentication Schemas
Pydantic models for authentication requests and responses
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class UserRegister(BaseModel):
    """Schema for user registration request"""
    nome: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    confirm_password: str = Field(..., min_length=6, description="Password confirmation")
    crm: Optional[str] = Field(None, description="CRM number (for doctors)")
    especialidade: Optional[str] = Field(None, description="Medical specialty (for doctors)")
    role: str = Field(default="user", description="User role: user, doctor, admin")

    def validate_passwords_match(self):
        """Validate that password and confirm_password match"""
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    """Schema for user data in responses"""
    id: int
    nome: str
    email: str
    role: str
    crm: Optional[str] = None
    especialidade: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class PasswordChange(BaseModel):
    """Schema for password change request"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")
    confirm_new_password: str = Field(..., min_length=6, description="New password confirmation")

    def validate_passwords_match(self):
        """Validate that new passwords match"""
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match")
        return self


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=6, description="New password")
    confirm_new_password: str = Field(..., min_length=6, description="New password confirmation")

    def validate_passwords_match(self):
        """Validate that new passwords match"""
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match")
        return self


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class AuthStatus(BaseModel):
    """Schema for authentication status"""
    is_authenticated: bool
    user: Optional[UserResponse] = None
    permissions: Optional[list] = None
