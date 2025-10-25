"""Tests for user management API endpoints."""

import re

from fastapi.testclient import TestClient

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import (
    TicketCreateCommand,
    TicketData,
    TicketPriority,
    UserRole,
)
from tests.conftest import client, test_repo  # noqa: F401
from tests.fixtures.auth_fixtures import (  # noqa: F401
    org_admin_token,
    super_admin_token,
    write_user_token,
)
from tests.helpers import auth_headers, create_test_org, create_test_project_via_repo, create_test_user


class TestCreateUser:
    """Tests for POST /api/users endpoint - REQ-USER-001, REQ-USER-002."""

    def test_create_user_as_super_admin(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test Super Admin creating user in any organization."""
        # Create org first
        org_id = create_test_org(test_repo, "Target Org")

        # Create user
        response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "admin"},
            json={"username": "newuser", "email": "new@example.com", "full_name": "New User"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["full_name"] == "New User"
        assert data["user"]["organization_id"] == org_id
        assert data["user"]["role"] == "admin"
        assert data["user"]["is_active"] is True
        assert "id" in data["user"]
        assert "created_at" in data["user"]

        # Verify generated password is returned
        assert "generated_password" in data
        password = data["generated_password"]
        assert len(password) >= 12
        # Verify password meets requirements
        assert re.search(r"[A-Z]", password) is not None  # Uppercase
        assert re.search(r"[a-z]", password) is not None  # Lowercase
        assert re.search(r"\d", password) is not None  # Digit
        assert re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]", password) is not None  # Special char

        # Verify user can login with generated password
        login_response = client.post("/auth/login", json={"username": "newuser", "password": password})
        assert login_response.status_code == 200

    def test_create_user_as_org_admin_in_own_org(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test Org Admin creating user in their own organization."""
        token, org_id = org_admin_token

        response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "write_access"},
            json={"username": "teamuser", "email": "team@example.com", "full_name": "Team User"},
            headers=auth_headers(token),
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user"]["username"] == "teamuser"
        assert data["user"]["organization_id"] == org_id
        assert data["user"]["role"] == "write_access"
        assert "generated_password" in data

    def test_create_user_as_org_admin_in_different_org_fails(
        self, client: TestClient, org_admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test Org Admin cannot create user in different organization."""
        token, org_id = org_admin_token

        # Create another org
        other_org_id = create_test_org(test_repo, "Other Org")

        response = client.post(
            "/api/users",
            params={"organization_id": other_org_id, "role": "admin"},
            json={"username": "baduser", "email": "bad@example.com", "full_name": "Bad User"},
            headers=auth_headers(token),
        )

        assert response.status_code == 403
        assert "own organization" in response.json()["detail"]

    def test_create_user_with_duplicate_username_fails(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test creating user with duplicate username fails."""
        org_id = create_test_org(test_repo)

        # Create first user
        response1 = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "admin"},
            json={"username": "duplicate", "email": "email1@example.com", "full_name": "User 1"},
            headers=auth_headers(super_admin_token),
        )
        assert response1.status_code == 201

        # Attempt to create second user with same username
        response2 = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "admin"},
            json={"username": "duplicate", "email": "email2@example.com", "full_name": "User 2"},
            headers=auth_headers(super_admin_token),
        )
        assert response2.status_code == 400
        assert "Username already exists" in response2.json()["detail"]

    def test_create_user_with_invalid_role_fails(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test creating user with invalid role fails validation."""
        org_id = create_test_org(test_repo)

        response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "invalid_role"},
            json={"username": "user1", "email": "user1@example.com", "full_name": "User 1"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 422  # Validation error

    def test_create_user_with_super_admin_role_fails(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test cannot assign super_admin role via API."""
        org_id = create_test_org(test_repo)

        response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "super_admin"},
            json={"username": "badadmin", "email": "bad@example.com", "full_name": "Bad Admin"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 400
        assert "super_admin" in response.json()["detail"].lower()

    def test_create_user_in_nonexistent_org_fails(self, client: TestClient, super_admin_token: str) -> None:
        """Test creating user in non-existent organization fails."""
        response = client.post(
            "/api/users",
            params={"organization_id": "nonexistent-org-id", "role": "admin"},
            json={"username": "user1", "email": "user1@example.com", "full_name": "User 1"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 400
        assert "Organization not found" in response.json()["detail"]

    def test_create_user_without_auth_fails(self, client: TestClient, test_repo: Repository) -> None:
        """Test creating user without authentication fails."""
        org_id = create_test_org(test_repo)

        response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "admin"},
            json={"username": "user1", "email": "user1@example.com", "full_name": "User 1"},
        )

        assert response.status_code == 401

    def test_create_user_as_regular_user_fails(self, client: TestClient, write_user_token: tuple[str, str]) -> None:
        """Test regular user cannot create users."""
        token, org_id = write_user_token

        response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "read_access"},
            json={"username": "newuser", "email": "new@example.com", "full_name": "New User"},
            headers=auth_headers(token),
        )

        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]


class TestGetUser:
    """Tests for GET /api/users/{id} endpoint - REQ-USER-007, REQ-USER-008."""

    def test_get_user_by_id_as_super_admin(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test Super Admin can get any user."""
        # Create org and user
        org_id = create_test_org(test_repo)
        user_id = create_test_user(
            test_repo,
            org_id,
            username="getme",
            email="getme@example.com",
            full_name="Get Me",
            role=UserRole.ADMIN,
            password="pass123",
        )

        response = client.get(f"/api/users/{user_id}", headers=auth_headers(super_admin_token))

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "getme"
        assert data["email"] == "getme@example.com"
        # Verify password is NOT exposed
        assert "password" not in data
        assert "password_hash" not in data

    def test_get_user_in_same_org(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test user can get another user in same organization."""
        token, org_id = org_admin_token

        # Create another user in same org using API
        create_response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "write_access"},
            json={"username": "teammate", "email": "team@example.com", "full_name": "Team Mate"},
            headers=auth_headers(token),
        )
        created_user_id = create_response.json()["user"]["id"]

        # Get the user
        response = client.get(f"/api/users/{created_user_id}", headers=auth_headers(token))

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user_id
        assert data["username"] == "teammate"

    def test_get_user_in_different_org_returns_404(
        self, client: TestClient, org_admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test user cannot access user from different organization (returns 404)."""
        token, org_id = org_admin_token

        # Create another org and user
        other_org_id = create_test_org(test_repo, "Other Org")
        other_user_id = create_test_user(test_repo, other_org_id)

        response = client.get(f"/api/users/{other_user_id}", headers=auth_headers(token))

        # Should return 404 to avoid leaking cross-org information
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_nonexistent_user_returns_404(self, client: TestClient, super_admin_token: str) -> None:
        """Test getting non-existent user returns 404."""
        response = client.get("/api/users/nonexistent-id", headers=auth_headers(super_admin_token))

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_user_without_auth_fails(self, client: TestClient, test_repo: Repository) -> None:
        """Test getting user without authentication fails."""
        # Create a user
        org_id = create_test_org(test_repo)
        user_id = create_test_user(test_repo, org_id)

        response = client.get(f"/api/users/{user_id}")

        assert response.status_code == 401


class TestListUsers:
    """Tests for GET /api/users endpoint - REQ-USER-006."""

    def test_list_users_as_super_admin_sees_all(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test Super Admin sees all users across all organizations."""
        # Create multiple orgs and users
        org1_id = create_test_org(test_repo, "Org 1")
        org2_id = create_test_org(test_repo, "Org 2")

        create_test_user(
            test_repo,
            org1_id,
            username="user1",
            email="user1@example.com",
            full_name="User 1",
            role=UserRole.ADMIN,
            password="pass",
        )
        create_test_user(
            test_repo,
            org2_id,
            username="user2",
            email="user2@example.com",
            full_name="User 2",
            role=UserRole.READ_ACCESS,
            password="pass",
        )

        response = client.get("/api/users", headers=auth_headers(super_admin_token))

        assert response.status_code == 200
        users = response.json()
        # Should include superadmin + user1 + user2 = 3
        assert len(users) >= 3
        usernames = {user["username"] for user in users}
        assert "user1" in usernames
        assert "user2" in usernames
        assert "superadmin" in usernames

    def test_list_users_as_org_admin_sees_only_own_org(
        self, client: TestClient, org_admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test Org Admin sees only users in their organization."""
        token, org_id = org_admin_token

        # Create user in same org
        create_test_user(
            test_repo,
            org_id,
            username="teammate",
            email="team@example.com",
            full_name="Team Mate",
            role=UserRole.WRITE_ACCESS,
            password="pass",
        )

        # Create user in different org
        other_org_id = create_test_org(test_repo, "Other Org")
        create_test_user(
            test_repo,
            other_org_id,
            username="outsider",
            email="out@example.com",
            full_name="Outsider",
            role=UserRole.ADMIN,
            password="pass",
        )

        response = client.get("/api/users", headers=auth_headers(token))

        assert response.status_code == 200
        users = response.json()
        usernames = {user["username"] for user in users}
        # Should include orgadmin and teammate, but not outsider
        assert "orgadmin" in usernames
        assert "teammate" in usernames
        assert "outsider" not in usernames

    def test_list_users_with_role_filter(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test filtering users by role."""
        org_id = create_test_org(test_repo)

        create_test_user(
            test_repo,
            org_id,
            username="admin1",
            email="admin1@example.com",
            full_name="Admin 1",
            role=UserRole.ADMIN,
            password="pass",
        )
        create_test_user(
            test_repo,
            org_id,
            username="reader1",
            email="reader1@example.com",
            full_name="Reader 1",
            role=UserRole.READ_ACCESS,
            password="pass",
        )

        response = client.get("/api/users", params={"role": "admin"}, headers=auth_headers(super_admin_token))

        assert response.status_code == 200
        users = response.json()
        # All returned users should be admins
        for user in users:
            assert user["role"] in ["admin", "super_admin"]

    def test_list_users_with_is_active_filter(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test filtering users by active status."""
        org_id = create_test_org(test_repo)

        # Create active user
        create_test_user(
            test_repo,
            org_id,
            username="active",
            email="active@example.com",
            full_name="Active User",
            role=UserRole.ADMIN,
            password="pass",
        )

        # Create and deactivate user
        inactive_user_id = create_test_user(
            test_repo,
            org_id,
            username="inactive",
            email="inactive@example.com",
            full_name="Inactive User",
            role=UserRole.ADMIN,
            password="pass",
        )
        from project_management_crud_example.domain_models import UserUpdateCommand

        test_repo.users.update(inactive_user_id, UserUpdateCommand(is_active=False))

        # Filter for active users
        response = client.get("/api/users", params={"is_active": "true"}, headers=auth_headers(super_admin_token))

        assert response.status_code == 200
        users = response.json()
        usernames = {user["username"] for user in users}
        assert "active" in usernames
        assert "inactive" not in usernames

    def test_list_users_without_auth_fails(self, client: TestClient) -> None:
        """Test listing users without authentication fails."""
        response = client.get("/api/users")

        assert response.status_code == 401


class TestUpdateUser:
    """Tests for PUT /api/users/{id} endpoint - REQ-USER-003, REQ-USER-004."""

    def test_update_user_as_super_admin(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test Super Admin can update any user."""
        org_id = create_test_org(test_repo)
        user_id = create_test_user(
            test_repo,
            org_id,
            username="updateme",
            email="old@example.com",
            full_name="Old Name",
            role=UserRole.WRITE_ACCESS,
            password="pass",
        )

        response = client.put(
            f"/api/users/{user_id}",
            json={"email": "new@example.com", "full_name": "New Name", "role": "project_manager"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New Name"
        assert data["role"] == "project_manager"
        # Verify unchanged fields
        assert data["username"] == "updateme"
        assert data["organization_id"] == org_id

    def test_update_user_partial_fields(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test updating only some user fields."""
        org_id = create_test_org(test_repo)
        user_id = create_test_user(
            test_repo,
            org_id,
            username="partial",
            email="partial@example.com",
            full_name="Partial User",
            role=UserRole.ADMIN,
            password="pass",
        )

        # Update only email
        response = client.put(
            f"/api/users/{user_id}",
            json={"email": "updated@example.com"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        # Verify other fields unchanged
        assert data["full_name"] == "Partial User"
        assert data["role"] == "admin"

    def test_deactivate_user(self, client: TestClient, super_admin_token: str, test_repo: Repository) -> None:
        """Test deactivating a user."""
        org_id = create_test_org(test_repo)
        user_id = create_test_user(
            test_repo,
            org_id,
            username="deactivateme",
            email="deactivate@example.com",
            full_name="Deactivate Me",
            role=UserRole.ADMIN,
            password="pass123",
        )

        # Deactivate
        response = client.put(
            f"/api/users/{user_id}",
            json={"is_active": False},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

        # Verify user cannot login
        login_response = client.post("/auth/login", json={"username": "deactivateme", "password": "pass123"})
        assert login_response.status_code == 401

    def test_reactivate_user(self, client: TestClient, super_admin_token: str, test_repo: Repository) -> None:
        """Test reactivating a user."""
        org_id = create_test_org(test_repo)
        user_id = create_test_user(
            test_repo,
            org_id,
            username="reactivateme",
            email="reactivate@example.com",
            full_name="Reactivate Me",
            role=UserRole.ADMIN,
            password="pass123",
        )

        # Deactivate first
        from project_management_crud_example.domain_models import UserUpdateCommand

        test_repo.users.update(user_id, UserUpdateCommand(is_active=False))

        # Reactivate via API
        response = client.put(
            f"/api/users/{user_id}",
            json={"is_active": True},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True

        # Verify user can login again
        login_response = client.post("/auth/login", json={"username": "reactivateme", "password": "pass123"})
        assert login_response.status_code == 200

    def test_update_user_as_org_admin_in_own_org(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test Org Admin can update users in their organization."""
        token, org_id = org_admin_token

        # Create user in same org via API
        create_response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "write_access"},
            json={"username": "updateable", "email": "update@example.com", "full_name": "Updateable User"},
            headers=auth_headers(token),
        )
        user_id = create_response.json()["user"]["id"]

        # Update the user
        response = client.put(
            f"/api/users/{user_id}",
            json={"full_name": "Updated Name"},
            headers=auth_headers(token),
        )

        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    def test_update_user_as_org_admin_in_different_org_fails(
        self, client: TestClient, org_admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test Org Admin cannot update users in different organization."""
        token, org_id = org_admin_token

        # Create user in different org
        other_org_id = create_test_org(test_repo, "Other Org")
        other_user_id = create_test_user(
            test_repo,
            other_org_id,
            username="other",
            email="other@example.com",
            full_name="Other User",
            role=UserRole.ADMIN,
            password="pass",
        )

        response = client.put(
            f"/api/users/{other_user_id}",
            json={"full_name": "Hacked Name"},
            headers=auth_headers(token),
        )

        assert response.status_code == 403
        assert "own organization" in response.json()["detail"]

    def test_update_user_with_super_admin_role_fails(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test cannot assign super_admin role via update."""
        org_id = create_test_org(test_repo)
        user_id = create_test_user(
            test_repo,
            org_id,
            username="user1",
            email="user1@example.com",
            full_name="User 1",
            role=UserRole.ADMIN,
            password="pass",
        )

        response = client.put(
            f"/api/users/{user_id}",
            json={"role": "super_admin"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 400
        assert "super_admin" in response.json()["detail"].lower()

    def test_update_nonexistent_user_returns_404(self, client: TestClient, super_admin_token: str) -> None:
        """Test updating non-existent user returns 404."""
        response = client.put(
            "/api/users/nonexistent-id",
            json={"full_name": "New Name"},
            headers=auth_headers(super_admin_token),
        )

        assert response.status_code == 404

    def test_update_user_as_regular_user_fails(
        self, client: TestClient, write_user_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test regular user cannot update users."""
        token, org_id = write_user_token

        # Create another user
        user_id = create_test_user(test_repo, org_id)

        response = client.put(
            f"/api/users/{user_id}",
            json={"full_name": "Hacked"},
            headers=auth_headers(token),
        )

        assert response.status_code == 403


class TestDeleteUser:
    """Tests for DELETE /api/users/{id} endpoint - REQ-USER-005."""

    def test_delete_user_as_super_admin(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test Super Admin can delete users."""
        org_id = create_test_org(test_repo)
        user_id = create_test_user(test_repo, org_id)

        response = client.delete(f"/api/users/{user_id}", headers=auth_headers(super_admin_token))

        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(f"/api/users/{user_id}", headers=auth_headers(super_admin_token))
        assert get_response.status_code == 404

    def test_delete_user_with_created_tickets_fails(
        self, client: TestClient, super_admin_token: str, test_repo: Repository
    ) -> None:
        """Test cannot delete user who has created tickets."""
        # Create org, user, project, and ticket
        org_id = create_test_org(test_repo)
        user_id = create_test_user(test_repo, org_id)
        project_id = create_test_project_via_repo(test_repo, org_id)
        test_repo.tickets.create(
            TicketCreateCommand(
                ticket_data=TicketData(title="Test Ticket", description="Test", priority=TicketPriority.MEDIUM),
                project_id=project_id,
                assignee_id=None,
            ),
            reporter_id=user_id,
        )

        response = client.delete(f"/api/users/{user_id}", headers=auth_headers(super_admin_token))

        assert response.status_code == 400
        assert "ticket" in response.json()["detail"].lower()

    def test_delete_user_as_org_admin_fails(
        self, client: TestClient, org_admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test Org Admin cannot delete users (Super Admin only)."""
        token, org_id = org_admin_token

        # Create user via API
        create_response = client.post(
            "/api/users",
            params={"organization_id": org_id, "role": "write_access"},
            json={"username": "deleteme", "email": "delete@example.com", "full_name": "Delete Me"},
            headers=auth_headers(token),
        )
        user_id = create_response.json()["user"]["id"]

        # Attempt to delete
        response = client.delete(f"/api/users/{user_id}", headers=auth_headers(token))

        assert response.status_code == 403
        assert "Super Admin" in response.json()["detail"]

    def test_delete_nonexistent_user_returns_404(self, client: TestClient, super_admin_token: str) -> None:
        """Test deleting non-existent user returns 404."""
        response = client.delete("/api/users/nonexistent-id", headers=auth_headers(super_admin_token))

        assert response.status_code == 404

    def test_delete_user_without_auth_fails(self, client: TestClient, test_repo: Repository) -> None:
        """Test deleting user without authentication fails."""
        org_id = create_test_org(test_repo)
        user_id = create_test_user(
            test_repo,
            org_id,
            username="user1",
            email="user1@example.com",
            full_name="User 1",
            role=UserRole.ADMIN,
            password="pass",
        )

        response = client.delete(f"/api/users/{user_id}")

        assert response.status_code == 401
