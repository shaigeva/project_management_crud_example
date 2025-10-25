"""Tests for system bootstrap functionality."""

import pytest

from project_management_crud_example.bootstrap_data import SUPER_ADMIN_PASSWORD, ensure_super_admin
from project_management_crud_example.config import settings
from project_management_crud_example.dal.sqlite.database import Database
from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import UserRole
from project_management_crud_example.utils.password import TestPasswordHasher
from tests.conftest import test_db  # noqa: F401


class TestBootstrapSuperAdmin:
    """Tests for Super Admin bootstrap functionality."""

    def test_bootstrap_creates_super_admin(self, test_db: Database) -> None:
        """Test that bootstrap creates Super Admin when none exists."""
        created, user_id = ensure_super_admin(test_db)

        assert created is True
        assert user_id is not None

        # Verify user was created
        with test_db.get_session() as session:
            repo = Repository(session, password_hasher=TestPasswordHasher())
            users = repo.users.get_all()
            super_admins = [u for u in users if u.role == UserRole.SUPER_ADMIN]

            assert len(super_admins) == 1
            admin = super_admins[0]
            assert admin.id == user_id
            assert admin.username == settings.BOOTSTRAP_ADMIN_USERNAME
            assert admin.email == settings.BOOTSTRAP_ADMIN_EMAIL
            assert admin.full_name == settings.BOOTSTRAP_ADMIN_FULL_NAME
            assert admin.organization_id is None  # Super Admin has no org
            assert admin.is_active is True

    def test_bootstrap_is_idempotent(self, test_db: Database) -> None:
        """Test that running bootstrap twice doesn't create duplicate admins."""
        # First run - should create
        created1, user_id1 = ensure_super_admin(test_db)
        assert created1 is True
        assert user_id1 is not None

        # Second run - should skip
        created2, user_id2 = ensure_super_admin(test_db)
        assert created2 is False
        assert user_id2 is None

        # Verify only one Super Admin exists
        with test_db.get_session() as session:
            repo = Repository(session, password_hasher=TestPasswordHasher())
            users = repo.users.get_all()
            super_admins = [u for u in users if u.role == UserRole.SUPER_ADMIN]
            assert len(super_admins) == 1

    def test_bootstrap_password_works_for_login(self, test_db: Database) -> None:
        """Test that constant password can be used for authentication."""
        created, user_id = ensure_super_admin(test_db)
        assert created is True
        assert user_id is not None

        # Get user auth data and verify constant password works
        password_hasher = TestPasswordHasher()  # Use test hasher since bootstrap used it in test mode
        with test_db.get_session() as session:
            repo = Repository(session, password_hasher=password_hasher)
            user_auth = repo.users.get_by_username_with_password(settings.BOOTSTRAP_ADMIN_USERNAME)

            assert user_auth is not None
            assert password_hasher.verify_password(SUPER_ADMIN_PASSWORD, user_auth.password_hash) is True

    def test_bootstrap_uses_constant_password(self, test_db: Database) -> None:
        """Test that bootstrap uses the constant password for development convenience."""
        created, user_id = ensure_super_admin(test_db)
        assert created is True

        # Verify the constant password is set correctly
        assert SUPER_ADMIN_PASSWORD == "SuperAdmin123!"  # Constant for example app
        assert len(SUPER_ADMIN_PASSWORD) >= 8  # Reasonable minimum

        # Verify it works for authentication
        password_hasher = TestPasswordHasher()  # Use test hasher since bootstrap used it in test mode
        with test_db.get_session() as session:
            repo = Repository(session, password_hasher=password_hasher)
            user_auth = repo.users.get_by_username_with_password(settings.BOOTSTRAP_ADMIN_USERNAME)
            assert user_auth is not None
            assert password_hasher.verify_password(SUPER_ADMIN_PASSWORD, user_auth.password_hash) is True

    def test_bootstrap_respects_env_configuration(self, test_db: Database, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that bootstrap uses environment configuration."""
        # Set custom values (need to reload settings after monkeypatch)
        monkeypatch.setenv("BOOTSTRAP_ADMIN_USERNAME", "customadmin")
        monkeypatch.setenv("BOOTSTRAP_ADMIN_EMAIL", "custom@example.com")
        monkeypatch.setenv("BOOTSTRAP_ADMIN_FULL_NAME", "Custom Administrator")

        # Reload settings to pick up new env vars
        from project_management_crud_example import config

        config.get_settings.cache_clear()

        created, user_id = ensure_super_admin(test_db)
        assert created is True

        # Verify custom values were used
        with test_db.get_session() as session:
            repo = Repository(session, password_hasher=TestPasswordHasher())
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
            repo = Repository(session, password_hasher=TestPasswordHasher())
            user_data = UserData(
                username="existing_admin",
                email="existing@example.com",
                full_name="Existing Admin",
            )
            command = UserCreateCommand(
                user_data=user_data,
                password="ExistingPassword123",
                organization_id=None,
                role=UserRole.SUPER_ADMIN,
            )
            repo.users.create(command)

        # Bootstrap should skip
        created, user_id = ensure_super_admin(test_db)
        assert created is False
        assert user_id is None

        # Verify no additional Super Admin was created
        with test_db.get_session() as session:
            repo = Repository(session, password_hasher=TestPasswordHasher())
            users = repo.users.get_all()
            super_admins = [u for u in users if u.role == UserRole.SUPER_ADMIN]
            assert len(super_admins) == 1
            assert super_admins[0].username == "existing_admin"
