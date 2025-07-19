"""
Hospital Management System - Authentication Router
FastAPI routes for user authentication and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from ..database.database import get_database
from .repository_auth import AuthRepository
from .schema_auth import (
    UserLogin, UserRegister, UserResponse, TokenResponse, TokenData,
    PasswordChange, PasswordReset, PasswordResetConfirm,
    RefreshTokenRequest, AuthStatus
)
from ..security import (
    create_access_token, create_refresh_token, verify_token,
    AuthenticationError, PermissionError,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> UserResponse:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if payload is None:
        raise AuthenticationError("Invalid or expired token")
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")
    
    auth_repo = AuthRepository(db)
    user = auth_repo.get_user_by_id(user_id)
    
    if user is None:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    
    return UserResponse.model_validate(user)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_database)
) -> Optional[UserResponse]:
    """Get current authenticated user (optional)"""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token, "access")
        
        if payload is None:
            return None
        
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        
        auth_repo = AuthRepository(db)
        user = auth_repo.get_user_by_id(user_id)
        
        if user is None or not user.is_active:
            return None
        
        return UserResponse.model_validate(user)
    except Exception:
        return None


def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("User account is inactive")
    return current_user


def check_permission(required_permission: str):
    """Dependency to check user permissions"""
    def permission_checker(
        current_user: UserResponse = Depends(get_current_active_user),
        db: Session = Depends(get_database)
    ):
        auth_repo = AuthRepository(db)
        permissions = auth_repo.get_user_permissions(current_user.id)
        
        if required_permission not in permissions:
            raise PermissionError(f"Permission '{required_permission}' required")
        
        return current_user
    
    return permission_checker


@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_database)):
    """Authenticate user and return access token"""
    auth_repo = AuthRepository(db)
    
    # Authenticate user
    user = auth_repo.authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }
    
    access_token = create_access_token(token_data, access_token_expires)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_database)):
    """Register a new user"""
    auth_repo = AuthRepository(db)
    
    try:
        user = auth_repo.create_user(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: RefreshTokenRequest, db: Session = Depends(get_database)):
    """Refresh access token using refresh token"""
    payload = verify_token(refresh_request.refresh_token, "refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user and verify still active
    auth_repo = AuthRepository(db)
    user = auth_repo.get_user_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }
    
    access_token = create_access_token(token_data, access_token_expires)
    new_refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.put("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Change user password"""
    auth_repo = AuthRepository(db)
    
    try:
        success = auth_repo.update_password(current_user.id, password_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/password-reset")
async def request_password_reset(reset_request: PasswordReset, db: Session = Depends(get_database)):
    """Request password reset token"""
    auth_repo = AuthRepository(db)
    
    token = auth_repo.create_password_reset_token(reset_request.email)
    if token:
        # In production, you would send this token via email
        # For now, we'll return it in the response (not secure for production)
        return {"message": "Password reset token created", "token": token}
    else:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset token has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_database)
):
    """Confirm password reset with token"""
    auth_repo = AuthRepository(db)
    
    try:
        reset_data.validate_passwords_match()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    success = auth_repo.reset_password_with_token(reset_data.token, reset_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}


@router.get("/status", response_model=AuthStatus)
async def get_auth_status(
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: Session = Depends(get_database)
):
    """Get authentication status"""
    if current_user:
        auth_repo = AuthRepository(db)
        permissions = auth_repo.get_user_permissions(current_user.id)
        return AuthStatus(
            is_authenticated=True,
            user=current_user,
            permissions=permissions
        )
    else:
        return AuthStatus(is_authenticated=False)


# Admin-only endpoints
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(check_permission("user:read")),
    db: Session = Depends(get_database)
):
    """Get all users (admin only)"""
    auth_repo = AuthRepository(db)
    users = auth_repo.get_all_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: UserResponse = Depends(check_permission("user:update")),
    db: Session = Depends(get_database)
):
    """Deactivate user account (admin only)"""
    auth_repo = AuthRepository(db)
    
    success = auth_repo.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: UserResponse = Depends(check_permission("user:update")),
    db: Session = Depends(get_database)
):
    """Activate user account (admin only)"""
    auth_repo = AuthRepository(db)
    
    success = auth_repo.activate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User activated successfully"}


@router.get("/users/role/{role}", response_model=List[UserResponse])
async def get_users_by_role(
    role: str,
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(check_permission("user:read")),
    db: Session = Depends(get_database)
):
    """Get users by role (admin only)"""
    auth_repo = AuthRepository(db)
    users = auth_repo.get_users_by_role(role, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]
