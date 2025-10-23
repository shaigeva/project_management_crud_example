"""Tests for user operations through Repository interface."""

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import UserCreateCommand, UserData, UserRole
from tests.conftest import test_repo  # noqa: F401


class TestUserOperations:
    """Test user operations through Repository interface."""

    def test_create_user(self, test_repo: Repository) -> None:
        """Test creating a user through repository."""
        user_data = UserData(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
        )
        command = UserCreateCommand(
            user_data=user_data,
            password="TestPassword123",
            organization_id="org-123",
            role=UserRole.ADMIN,
        )

        user = test_repo.users.create(command)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.organization_id == "org-123"
        assert user.role == UserRole.ADMIN
        assert user.is_active is True
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None
        # Verify password_hash is NOT exposed in domain model
        assert not hasattr(user, "password_hash")

    def test_create_super_admin_without_organization(self, test_repo: Repository) -> None:
        """Test creating Super Admin user without organization."""
        user_data = UserData(
            username="superadmin",
            email="admin@example.com",
            full_name="Super Administrator",
        )
        command = UserCreateCommand(
            user_data=user_data,
            password="TestPassword123",
            organization_id=None,
            role=UserRole.SUPER_ADMIN,
        )

        user = test_repo.users.create(command)

        assert user.username == "superadmin"
        assert user.organization_id is None
        assert user.role == UserRole.SUPER_ADMIN
        assert user.id is not None

    def test_get_user_by_id(self, test_repo: Repository) -> None:
        """Test retrieving user by ID through repository."""
        # Create user
        user_data = UserData(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
        )
        command = UserCreateCommand(
            user_data=user_data,
            password="TestPassword123",
            organization_id="org-123",
            role=UserRole.ADMIN,
        )
        created_user = test_repo.users.create(command)

        # Retrieve user
        retrieved_user = test_repo.users.get_by_id(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "testuser"
        assert retrieved_user.email == "test@example.com"

    def test_get_user_by_id_not_found(self, test_repo: Repository) -> None:
        """Test retrieving non-existent user returns None."""
        retrieved_user = test_repo.users.get_by_id("non-existent-id")

        assert retrieved_user is None

    def test_get_user_by_username(self, test_repo: Repository) -> None:
        """Test retrieving user by username through repository."""
        # Create user
        user_data = UserData(
            username="findme",
            email="findme@example.com",
            full_name="Find Me",
        )
        command = UserCreateCommand(
            user_data=user_data,
            password="TestPassword123",
            organization_id="org-123",
            role=UserRole.WRITE_ACCESS,
        )
        created_user = test_repo.users.create(command)

        # Retrieve by username
        retrieved_user = test_repo.users.get_by_username("findme")

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "findme"

    def test_get_user_by_username_not_found(self, test_repo: Repository) -> None:
        """Test retrieving user by non-existent username returns None."""
        retrieved_user = test_repo.users.get_by_username("nonexistent")

        assert retrieved_user is None

    def test_get_all_users(self, test_repo: Repository) -> None:
        """Test retrieving all users through repository."""
        # Create multiple users
        user1_data = UserData(username="user1", email="user1@example.com", full_name="User 1")
        user2_data = UserData(username="user2", email="user2@example.com", full_name="User 2")

        test_repo.users.create(
            UserCreateCommand(
                user_data=user1_data, password="TestPassword123", organization_id="org-123", role=UserRole.ADMIN
            )
        )
        test_repo.users.create(
            UserCreateCommand(
                user_data=user2_data, password="TestPassword123", organization_id="org-456", role=UserRole.READ_ACCESS
            )
        )

        # Get all users
        all_users = test_repo.users.get_all()

        assert len(all_users) == 2
        usernames = {user.username for user in all_users}
        assert usernames == {"user1", "user2"}

    def test_get_all_users_empty(self, test_repo: Repository) -> None:
        """Test retrieving all users when database is empty."""
        all_users = test_repo.users.get_all()

        assert all_users == []

    def test_delete_user(self, test_repo: Repository) -> None:
        """Test deleting a user through repository."""
        # Create user
        user_data = UserData(
            username="deleteme",
            email="deleteme@example.com",
            full_name="Delete Me",
        )
        command = UserCreateCommand(
            user_data=user_data,
            password="TestPassword123",
            organization_id="org-123",
            role=UserRole.WRITE_ACCESS,
        )
        created_user = test_repo.users.create(command)

        # Delete user
        success = test_repo.users.delete(created_user.id)

        assert success is True

        # Verify user is gone
        retrieved_user = test_repo.users.get_by_id(created_user.id)
        assert retrieved_user is None

    def test_delete_user_not_found(self, test_repo: Repository) -> None:
        """Test deleting non-existent user returns False."""
        success = test_repo.users.delete("non-existent-id")

        assert success is False
