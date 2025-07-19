"""
Hospital Management System - Authentication Repository
Database operations for user authentication and management
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from datetime import datetime, timedelta
import secrets

from ..model.models import Medico, Usuario
from ..security import verify_password, hash_password
from .schema_auth import UserRegister, PasswordChange


class AuthRepository:
    """Repository for authentication operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[Usuario]:
        """Get user by email address"""
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        """Get user by ID"""
        return self.db.query(Usuario).filter(Usuario.id == user_id).first()

    def get_doctor_by_email(self, email: str) -> Optional[Medico]:
        """Get doctor by email address"""
        return self.db.query(Medico).filter(Medico.email == email).first()

    def authenticate_user(self, email: str, password: str) -> Optional[Usuario]:
        """Authenticate user with email and password"""
        # First check in users table
        user = self.get_user_by_email(email)
        if user and verify_password(password, user.senha):
            return user
        
        # If not found, check in doctors table (for backward compatibility)
        doctor = self.get_doctor_by_email(email)
        if doctor and verify_password(password, doctor.senha):
            # Convert doctor to user format for consistency
            user_data = Usuario(
                id=doctor.id,
                nome=doctor.nome,
                email=doctor.email,
                senha=doctor.senha,
                role="doctor",
                crm=doctor.crm,
                especialidade=doctor.especialidade,
                is_active=True,
                created_at=datetime.utcnow()
            )
            return user_data
        
        return None

    def create_user(self, user_data: UserRegister) -> Usuario:
        """Create a new user"""
        # Validate passwords match
        user_data.validate_passwords_match()
        
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        # Check if doctor with this email exists
        if self.get_doctor_by_email(user_data.email):
            raise ValueError("Email already registered as doctor")
        
        # Create new user
        db_user = Usuario(
            nome=user_data.nome,
            email=user_data.email,
            senha=hash_password(user_data.password),
            role=user_data.role,
            crm=user_data.crm,
            especialidade=user_data.especialidade,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_password(self, user_id: int, password_data: PasswordChange) -> bool:
        """Update user password"""
        password_data.validate_passwords_match()
        
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not verify_password(password_data.current_password, user.senha):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.senha = hash_password(password_data.new_password)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

    def activate_user(self, user_id: int) -> bool:
        """Activate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Get all users with pagination"""
        return self.db.query(Usuario).offset(skip).limit(limit).all()

    def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Get users by role with pagination"""
        return self.db.query(Usuario).filter(Usuario.role == role).offset(skip).limit(limit).all()

    def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create password reset token for user"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Store token with expiration (24 hours)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return token

    def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        user = self.db.query(Usuario).filter(
            and_(
                Usuario.reset_token == token,
                Usuario.reset_token_expires > datetime.utcnow()
            )
        ).first()
        
        if not user:
            return False
        
        # Update password and clear reset token
        user.senha = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True

    def clear_expired_reset_tokens(self):
        """Clear expired password reset tokens"""
        self.db.query(Usuario).filter(
            Usuario.reset_token_expires < datetime.utcnow()
        ).update({
            Usuario.reset_token: None,
            Usuario.reset_token_expires: None,
            Usuario.updated_at: datetime.utcnow()
        })
        self.db.commit()

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get user permissions based on role"""
        user = self.get_user_by_id(user_id)
        if not user:
            return []
        
        # Define permissions by role
        permissions = {
            "admin": [
                "user:create", "user:read", "user:update", "user:delete",
                "doctor:create", "doctor:read", "doctor:update", "doctor:delete",
                "patient:create", "patient:read", "patient:update", "patient:delete",
                "room:create", "room:read", "room:update", "room:delete",
                "admission:create", "admission:read", "admission:update", "admission:delete",
                "system:manage"
            ],
            "doctor": [
                "doctor:read", "doctor:update",
                "patient:create", "patient:read", "patient:update",
                "admission:create", "admission:read", "admission:update",
                "room:read"
            ],
            "nurse": [
                "patient:read", "patient:update",
                "admission:read", "admission:update",
                "room:read"
            ],
            "user": [
                "patient:read",
                "doctor:read"
            ]
        }
        
        return permissions.get(user.role, permissions["user"])
