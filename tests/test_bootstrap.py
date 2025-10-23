"""Tests for system bootstrap functionality."""

import pytest

from project_management_crud_example.bootstrap import bootstrap_super_admin
from project_management_crud_example.config import settings
from project_management_crud_example.dal.sqlite.database import Database
from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import UserRole
from project_management_crud_example.utils.password import verify_password
from tests.conftest import test_db  # noqa: F401


class TestBootstrapSuperAdmin:
    """Tests for Super Admin bootstrap functionality."""

    def test_bootstrap_creates_super_admin(self, test_db: Database) -> None:
        """Test that bootstrap creates Super Admin when none exists."""
        created, password = bootstrap_super_admin(test_db)

        assert created is True
        assert password is not None
        assert len(password) >= 12  # Generated passwords are at least 12 chars

        # Verify user was created
        with test_db.get_session() as session:
            repo = Repository(session)
            users = repo.users.get_all()
            super_admins = [u for u in users if u.role == UserRole.SUPER_ADMIN]

            assert len(super_admins) == 1
            admin = super_admins[0]
            assert admin.username == settings.BOOTSTRAP_ADMIN_USERNAME
            assert admin.email == settings.BOOTSTRAP_ADMIN_EMAIL
            assert admin.full_name == settings.BOOTSTRAP_ADMIN_FULL_NAME
            assert admin.organization_id is None  # Super Admin has no org
            assert admin.is_active is True

    def test_bootstrap_is_idempotent(self, test_db: Database) -> None:
        """Test that running bootstrap twice doesn't create duplicate admins."""
        # First run - should create
        created1, password1 = bootstrap_super_admin(test_db)
        assert created1 is True
        assert password1 is not None

        # Second run - should skip
        created2, password2 = bootstrap_super_admin(test_db)
        assert created2 is False
        assert password2 is None

        # Verify only one Super Admin exists
        with test_db.get_session() as session:
            repo = Repository(session)
            users = repo.users.get_all()
            super_admins = [u for u in users if u.role == UserRole.SUPER_ADMIN]
            assert len(super_admins) == 1

    def test_bootstrap_password_works_for_login(self, test_db: Database) -> None:
        """Test that generated password can be used for authentication."""
        created, password = bootstrap_super_admin(test_db)
        assert created is True
        assert password is not None

        # Get user auth data and verify password
        with test_db.get_session() as session:
            repo = Repository(session)
            user_auth = repo.users.get_by_username_with_password(settings.BOOTSTRAP_ADMIN_USERNAME)

            assert user_auth is not None
            assert verify_password(password, user_auth.password_hash) is True

    def test_bootstrap_generates_random_password(self, test_db: Database) -> None:
        """Test that password is randomly generated (not a default)."""
        created, password = bootstrap_super_admin(test_db)
        assert created is True
        assert password is not None

        # Password should not be any common default
        common_defaults = ["password", "admin", "123456", "admin123", "Password1"]
        assert password not in common_defaults

        # Password should have sufficient length and complexity
        assert len(password) >= 12
        # Our generator creates passwords with letters and numbers
        assert any(c.isalpha() for c in password)
        assert any(c.isdigit() for c in password)

    def test_bootstrap_respects_env_configuration(self, test_db: Database, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that bootstrap uses environment configuration."""
        # Set custom values (need to reload settings after monkeypatch)
        monkeypatch.setenv("BOOTSTRAP_ADMIN_USERNAME", "customadmin")
        monkeypatch.setenv("BOOTSTRAP_ADMIN_EMAIL", "custom@example.com")
        monkeypatch.setenv("BOOTSTRAP_ADMIN_FULL_NAME", "Custom Administrator")

        # Reload settings to pick up new env vars
        from project_management_crud_example import config

        config.get_settings.cache_clear()

        created, password = bootstrap_super_admin(test_db)
        assert created is True

        # Verify custom values were used
        with test_db.get_session() as session:
            repo = Repository(session)
            user = repo.users.get_by_username("customadmin")

            assert user is not None
            assert user.username == "customadmin"
            assert user.email == "custom@example.com"
            assert user.full_name == "Custom Administrator"

        # Cleanup: restore settings
        config.get_settings.cache_clear()

    def test_bootstrap_skips_if_any_super_admin_exists(self, test_db: Database) -> None:
        """Test that bootstrap skips creation if any Super Admin exists."""
        # Manually create a Super Admin with different username
        from project_management_crud_example.domain_models import UserCreateCommand, UserData

        with test_db.get_session() as session:
            repo = Repository(session)
            user_data = UserData(
                username="existing_admin",
                email="existing@example.com",
                full_name="Existing Admin",
            )
            command = UserCreateCommand(
                user_data=user_data,
                organization_id=None,
                role=UserRole.SUPER_ADMIN,
            )
            repo.users.create(command)

        # Bootstrap should skip
        created, password = bootstrap_super_admin(test_db)
        assert created is False
        assert password is None

        # Verify no additional Super Admin was created
        with test_db.get_session() as session:
            repo = Repository(session)
            users = repo.users.get_all()
            super_admins = [u for u in users if u.role == UserRole.SUPER_ADMIN]
            assert len(super_admins) == 1
            assert super_admins[0].username == "existing_admin"
