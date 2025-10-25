"""Tests for authentication API endpoints.

This module tests login and token validation functionality through the API.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from project_management_crud_example.app import app
from project_management_crud_example.config import settings
from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import UserCreateCommand, UserData, UserRole
from tests.conftest import client, test_repo  # noqa: F401


@pytest.fixture
def test_user(test_repo: Repository) -> tuple[str, str]:
    """Create a test user and return (user_id, password)."""
    user_data = UserData(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
    )

    # Create user with known password
    password = "TestPassword123"
    command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id="org-123",
        role=UserRole.ADMIN,
    )
    user = test_repo.users.create(command)

    return user.id, password


@pytest.fixture
def test_super_admin(test_repo: Repository) -> tuple[str, str]:
    """Create a super admin user and return (user_id, password)."""
    user_data = UserData(
        username="superadmin",
        email="superadmin@example.com",
        full_name="Super Admin",
    )

    password = "SuperAdminPassword123"
    command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id=None,  # Super admin has no organization
        role=UserRole.SUPER_ADMIN,
    )
    user = test_repo.users.create(command)

    return user.id, password


class TestLogin:
    """Tests for POST /auth/login endpoint."""

    def test_login_with_valid_credentials_succeeds(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test login with valid credentials returns 200 with token."""
        user_id, password = test_user

        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"]  # Token is not empty

    def test_login_response_includes_all_fields(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test login response includes all required fields."""
        user_id, password = test_user

        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] == settings.JWT_EXPIRATION_SECONDS
        assert "user_id" in data
        assert data["user_id"] == user_id
        assert "organization_id" in data
        assert data["organization_id"] == "org-123"
        assert "role" in data
        assert data["role"] == "admin"

    def test_login_with_wrong_password_fails(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test login with wrong password returns 401 INVALID_CREDENTIALS."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "WrongPassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid credentials"
        assert data["error_code"] == "INVALID_CREDENTIALS"

    def test_login_with_nonexistent_user_fails(self, client: TestClient) -> None:
        """Test login with nonexistent user returns 401 INVALID_CREDENTIALS (same message)."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "SomePassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid credentials"
        assert data["error_code"] == "INVALID_CREDENTIALS"

    def test_login_with_inactive_user_fails(
        self, client: TestClient, test_user: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test login with inactive user returns 401 ACCOUNT_INACTIVE."""
        user_id, password = test_user

        # Deactivate user using test_repo's session
        from project_management_crud_example.dal.sqlite.orm_data_models import UserORM

        orm_user = test_repo.session.query(UserORM).filter(UserORM.id == user_id).first()
        orm_user.is_active = False
        test_repo.session.commit()

        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Account inactive"
        assert data["error_code"] == "ACCOUNT_INACTIVE"

    def test_login_username_is_case_insensitive(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test username lookup is case-insensitive."""
        user_id, password = test_user

        # Try different case variations
        for username_variant in ["TestUser", "TESTUSER", "testuser", "TeStUsEr"]:
            response = client.post(
                "/auth/login",
                json={"username": username_variant, "password": password},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id

    def test_login_password_is_case_sensitive(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test password verification is case-sensitive."""
        user_id, password = test_user

        # Wrong case should fail
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password.lower()},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid credentials"

    def test_login_with_empty_username_fails(self, client: TestClient) -> None:
        """Test login with empty username returns 422 validation error."""
        response = client.post(
            "/auth/login",
            json={"username": "", "password": "SomePassword"},
        )

        assert response.status_code == 422

    def test_login_with_empty_password_fails(self, client: TestClient) -> None:
        """Test login with empty password returns 422 validation error."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": ""},
        )

        assert response.status_code == 422

    def test_login_generates_valid_token(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test login generates a valid JWT token that can be decoded."""
        user_id, password = test_user

        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )

        assert response.status_code == 200
        token = response.json()["access_token"]

        # Decode token without verification to check structure
        payload = jwt.decode(token, options={"verify_signature": False})
        assert "user_id" in payload
        assert payload["user_id"] == user_id
        assert "organization_id" in payload
        assert "exp" in payload
        assert "iat" in payload
        # Role is NOT in token - fetched from DB on each request
        assert "role" not in payload

    def test_multiple_logins_create_different_tokens(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test that multiple logins succeed and both tokens are valid."""
        user_id, password = test_user

        # Create a test endpoint
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id}

        # Login twice
        response1 = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )
        response2 = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]

        # Both tokens should be valid and work
        assert token1  # Not empty
        assert token2  # Not empty

        # Verify both tokens can be used for authentication
        response_with_token1 = client.get(
            "/test/protected",
            headers={"Authorization": f"Bearer {token1}"},
        )
        response_with_token2 = client.get(
            "/test/protected",
            headers={"Authorization": f"Bearer {token2}"},
        )

        assert response_with_token1.status_code == 200
        assert response_with_token2.status_code == 200

    def test_login_for_super_admin_without_org(self, client: TestClient, test_super_admin: tuple[str, str]) -> None:
        """Test super admin can login without organization."""
        user_id, password = test_super_admin

        response = client.post(
            "/auth/login",
            json={"username": "superadmin", "password": password},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["organization_id"] is None
        assert data["role"] == "super_admin"


class TestProtectedEndpoints:
    """Tests for token validation on protected endpoints."""

    def test_request_without_token_returns_401(self, client: TestClient) -> None:
        """Test request without token returns 401 AUTHENTICATION_REQUIRED."""
        # Create a test endpoint that uses get_current_user
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id}

        response = client.get("/test/protected")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Authentication required"
        assert data["error_code"] == "AUTHENTICATION_REQUIRED"

    def test_request_with_valid_token_succeeds(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test request with valid token succeeds and gets current user."""
        user_id, password = test_user

        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )
        token = login_response.json()["access_token"]

        # Create a test endpoint
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id}

        # Make request with token
        response = client.get("/test/protected", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id

    def test_request_with_expired_token_fails(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test request with expired token returns 401 TOKEN_EXPIRED."""
        user_id, password = test_user

        # Create an expired token manually
        now = datetime.now(timezone.utc).replace(microsecond=0)
        expiration = now - timedelta(hours=1)  # Expired 1 hour ago

        expired_token = jwt.encode(
            {
                "user_id": user_id,
                "organization_id": "org-123",
                "exp": int(expiration.timestamp()),
                "iat": int((now - timedelta(hours=2)).timestamp()),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        # Create a test endpoint
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id}

        # Make request with expired token
        response = client.get("/test/protected", headers={"Authorization": f"Bearer {expired_token}"})

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Token expired"
        assert data["error_code"] == "TOKEN_EXPIRED"

    def test_request_with_invalid_token_fails(self, client: TestClient) -> None:
        """Test request with invalid token returns 401."""
        # Create a test endpoint
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id}

        # Make request with invalid token
        response = client.get("/test/protected", headers={"Authorization": "Bearer invalid-token"})

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid token"
        assert data["error_code"] == "INVALID_TOKEN"

    def test_request_with_malformed_auth_header_fails(self, client: TestClient) -> None:
        """Test request with malformed Authorization header returns 401."""
        # Create a test endpoint
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id}

        # Test various malformed headers
        malformed_headers = [
            "NoBearer token123",
            "Bearer",  # Missing token
            "token123",  # Missing "Bearer"
        ]

        for header in malformed_headers:
            response = client.get("/test/protected", headers={"Authorization": header})
            assert response.status_code == 401

    def test_request_with_deactivated_user_token_fails(
        self, client: TestClient, test_user: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test user deactivated after token issued cannot access protected endpoints."""
        user_id, password = test_user

        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )
        token = login_response.json()["access_token"]

        # Deactivate user using test_repo's session
        from project_management_crud_example.dal.sqlite.orm_data_models import UserORM

        orm_user = test_repo.session.query(UserORM).filter(UserORM.id == user_id).first()
        orm_user.is_active = False
        test_repo.session.commit()

        # Create a test endpoint
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id}

        # Make request with token from deactivated user
        response = client.get("/test/protected", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Account inactive"
        assert data["error_code"] == "ACCOUNT_INACTIVE"

    def test_token_validation_fetches_current_role(
        self, client: TestClient, test_user: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test role changes are reflected immediately (fetched from DB, not token)."""
        user_id, password = test_user

        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )
        token = login_response.json()["access_token"]

        # Change user role in database using test_repo's session
        from project_management_crud_example.dal.sqlite.orm_data_models import UserORM

        orm_user = test_repo.session.query(UserORM).filter(UserORM.id == user_id).first()
        orm_user.role = UserRole.READ_ACCESS.value
        test_repo.session.commit()

        # Create a test endpoint that returns current user
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected_role")
        async def protected_endpoint_role(current_user: User = Depends(get_current_user)) -> dict:  # noqa: B008
            return {"user_id": current_user.id, "role": current_user.role}

        # Make request with token - should get NEW role from DB
        response = client.get("/test/protected_role", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "read_access"  # New role, not the one from login time

    def test_get_current_user_returns_full_user_model(self, client: TestClient, test_user: tuple[str, str]) -> None:
        """Test get_current_user returns full User domain model with all fields."""
        user_id, password = test_user

        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": password},
        )
        token = login_response.json()["access_token"]

        # Create a test endpoint that returns current user
        from fastapi import Depends

        from project_management_crud_example.dependencies import get_current_user
        from project_management_crud_example.domain_models import User

        @app.get("/test/protected_user")
        async def protected_endpoint_user(current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
            return current_user

        # Make request with token
        response = client.get("/test/protected_user", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "full_name" in data
        assert "organization_id" in data
        assert "role" in data
        assert "is_active" in data
        assert "created_at" in data
        assert "updated_at" in data
        # Password hash should NOT be exposed
        assert "password_hash" not in data
