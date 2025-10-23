"""Tests for ORM to domain model converters."""

from sqlalchemy.orm import Session

from project_management_crud_example.dal.sqlite.converters import orm_user_to_domain_user
from project_management_crud_example.dal.sqlite.orm_data_models import UserORM
from project_management_crud_example.domain_models import UserRole
from project_management_crud_example.utils.password import hash_password
from tests.conftest import test_db, test_session  # noqa: F401


class TestUserConverter:
    """Tests for ORM to domain User converter."""

    def test_orm_to_domain_user_excludes_password_hash(self, test_session: Session) -> None:
        """Test that domain User doesn't include password_hash."""
        password_hash = hash_password("test_password_123")

        user_orm = UserORM(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password_hash=password_hash,
            organization_id="org-123",
            role=UserRole.ADMIN.value,
        )
        test_session.add(user_orm)
        test_session.commit()
        test_session.refresh(user_orm)

        # Convert to domain User
        domain_user = orm_user_to_domain_user(user_orm)

        # Verify conversion
        assert domain_user.id == user_orm.id
        assert domain_user.username == "testuser"
        assert domain_user.email == "test@example.com"
        assert domain_user.full_name == "Test User"
        assert domain_user.organization_id == "org-123"
        assert domain_user.role == UserRole.ADMIN
        assert domain_user.is_active is True

        # Verify password_hash is NOT in domain User
        assert not hasattr(domain_user, "password_hash")

    def test_orm_to_domain_user_with_null_organization(self, test_session: Session) -> None:
        """Test conversion for Super Admin with no organization."""
        password_hash = hash_password("admin_password")

        user_orm = UserORM(
            username="superadmin",
            email="admin@example.com",
            full_name="Super Admin",
            password_hash=password_hash,
            organization_id=None,
            role=UserRole.SUPER_ADMIN.value,
        )
        test_session.add(user_orm)
        test_session.commit()
        test_session.refresh(user_orm)

        domain_user = orm_user_to_domain_user(user_orm)

        assert domain_user.organization_id is None
        assert domain_user.role == UserRole.SUPER_ADMIN
