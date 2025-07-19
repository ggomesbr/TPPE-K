"""
Hospital Management System - Authentication Tests
Tests for authentication functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..main import app
from ..database.database import get_database
from ..model.models import Base, Usuario
from ..security import hash_password, create_access_token, verify_token
from .repository_auth import AuthRepository


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_database():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = override_get_database
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create database session for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "nome": "João Silva",
        "email": "joao.silva@hospital.com",
        "password": "senha123",
        "confirm_password": "senha123",
        "role": "doctor",
        "crm": "12345-SP",
        "especialidade": "Cardiologia"
    }


@pytest.fixture
def create_test_user(db_session):
    """Create a test user in database"""
    user = Usuario(
        nome="Test User",
        email="test@hospital.com",
        senha=hash_password("testpass123"),
        role="user",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestAuthRepository:
    """Test authentication repository functions"""

    def test_create_user(self, db_session, test_user_data):
        """Test user creation"""
        from .schema_auth import UserRegister
        
        auth_repo = AuthRepository(db_session)
        user_data = UserRegister(**test_user_data)
        
        user = auth_repo.create_user(user_data)
        
        assert user.nome == test_user_data["nome"]
        assert user.email == test_user_data["email"]
        assert user.role == test_user_data["role"]
        assert user.crm == test_user_data["crm"]
        assert user.is_active is True

    def test_create_user_duplicate_email(self, db_session, test_user_data, create_test_user):
        """Test user creation with duplicate email"""
        from .schema_auth import UserRegister
        
        auth_repo = AuthRepository(db_session)
        test_user_data["email"] = create_test_user.email
        user_data = UserRegister(**test_user_data)
        
        with pytest.raises(ValueError, match="Email already registered"):
            auth_repo.create_user(user_data)

    def test_authenticate_user_success(self, db_session, create_test_user):
        """Test successful user authentication"""
        auth_repo = AuthRepository(db_session)
        
        user = auth_repo.authenticate_user("test@hospital.com", "testpass123")
        
        assert user is not None
        assert user.email == "test@hospital.com"

    def test_authenticate_user_wrong_password(self, db_session, create_test_user):
        """Test authentication with wrong password"""
        auth_repo = AuthRepository(db_session)
        
        user = auth_repo.authenticate_user("test@hospital.com", "wrongpassword")
        
        assert user is None

    def test_authenticate_user_not_found(self, db_session):
        """Test authentication with non-existent user"""
        auth_repo = AuthRepository(db_session)
        
        user = auth_repo.authenticate_user("nonexistent@hospital.com", "password")
        
        assert user is None

    def test_get_user_by_email(self, db_session, create_test_user):
        """Test getting user by email"""
        auth_repo = AuthRepository(db_session)
        
        user = auth_repo.get_user_by_email("test@hospital.com")
        
        assert user is not None
        assert user.email == "test@hospital.com"

    def test_update_password(self, db_session, create_test_user):
        """Test password update"""
        from .schema_auth import PasswordChange
        
        auth_repo = AuthRepository(db_session)
        password_data = PasswordChange(
            current_password="testpass123",
            new_password="newpass123",
            confirm_new_password="newpass123"
        )
        
        success = auth_repo.update_password(create_test_user.id, password_data)
        
        assert success is True
        
        # Verify new password works
        user = auth_repo.authenticate_user("test@hospital.com", "newpass123")
        assert user is not None

    def test_deactivate_user(self, db_session, create_test_user):
        """Test user deactivation"""
        auth_repo = AuthRepository(db_session)
        
        success = auth_repo.deactivate_user(create_test_user.id)
        
        assert success is True
        
        # Verify user is deactivated
        user = auth_repo.get_user_by_id(create_test_user.id)
        assert user.is_active is False


class TestAuthAPI:
    """Test authentication API endpoints"""

    def test_register_user(self, setup_database, test_user_data):
        """Test user registration endpoint"""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == test_user_data["nome"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == test_user_data["role"]

    def test_login_success(self, setup_database, test_user_data):
        """Test successful login"""
        # First register user
        client.post("/api/auth/register", json=test_user_data)
        
        # Then login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_wrong_password(self, setup_database, test_user_data):
        """Test login with wrong password"""
        # First register user
        client.post("/api/auth/register", json=test_user_data)
        
        # Then login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401

    def test_get_current_user(self, setup_database, test_user_data):
        """Test getting current user info"""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]

    def test_change_password(self, setup_database, test_user_data):
        """Test password change"""
        # Register and login
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Change password
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123"
        }
        response = client.put("/api/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 200

    def test_protected_endpoint_without_token(self, setup_database):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403

    def test_protected_endpoint_invalid_token(self, setup_database):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401


class TestJWTSecurity:
    """Test JWT token functionality"""

    def test_create_and_verify_access_token(self):
        """Test JWT token creation and verification"""
        data = {"user_id": 1, "email": "test@hospital.com", "role": "user"}
        
        token = create_access_token(data)
        payload = verify_token(token, "access")
        
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["email"] == "test@hospital.com"
        assert payload["role"] == "user"

    def test_expired_token(self):
        """Test expired token verification"""
        data = {"user_id": 1, "email": "test@hospital.com", "role": "user"}
        expired_delta = timedelta(seconds=-1)  # Already expired
        
        token = create_access_token(data, expired_delta)
        payload = verify_token(token)
        
        assert payload is None

    def test_wrong_token_type(self):
        """Test token with wrong type"""
        from ..security import create_refresh_token
        
        data = {"user_id": 1, "email": "test@hospital.com", "role": "user"}
        refresh_token = create_refresh_token(data)
        
        # Try to verify refresh token as access token
        payload = verify_token(refresh_token, "access")
        
        assert payload is None
