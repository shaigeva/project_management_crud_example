"""Tests for ORM to domain model converters."""

from sqlalchemy.orm import Session

from project_management_crud_example.dal.sqlite.converters import (
    orm_ticket_to_domain_ticket,
    orm_user_to_domain_user,
)
from project_management_crud_example.dal.sqlite.orm_data_models import TicketORM, UserORM
from project_management_crud_example.domain_models import TicketPriority, TicketStatus, UserRole
from tests.conftest import test_db, test_session  # noqa: F401


class TestUserConverter:
    """Tests for ORM to domain User converter."""

    def test_orm_to_domain_user_excludes_password_hash(self, test_session: Session) -> None:
        """Test that domain User doesn't include password_hash."""
        # Use fake hash for converter tests - no need for real password hashing
        password_hash = "fake_hash_for_converter_test"

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
        # Use fake hash for converter tests - no need for real password hashing
        password_hash = "fake_hash_for_converter_test"

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


class TestTicketConverter:
    """Tests for ORM to domain Ticket converter."""

    def test_orm_to_domain_ticket_with_all_fields(self, test_session: Session) -> None:
        """Test converting ticket ORM with all fields to domain model."""
        ticket_orm = TicketORM(
            title="Test Ticket",
            description="Test description",
            status=TicketStatus.IN_PROGRESS.value,
            priority=TicketPriority.HIGH.value,
            assignee_id="user-123",
            reporter_id="user-456",
            project_id="project-789",
        )
        test_session.add(ticket_orm)
        test_session.commit()
        test_session.refresh(ticket_orm)

        # Convert to domain Ticket
        domain_ticket = orm_ticket_to_domain_ticket(ticket_orm)

        # Verify conversion
        assert domain_ticket.id == ticket_orm.id
        assert domain_ticket.title == "Test Ticket"
        assert domain_ticket.description == "Test description"
        assert domain_ticket.status == TicketStatus.IN_PROGRESS
        assert domain_ticket.priority == TicketPriority.HIGH
        assert domain_ticket.assignee_id == "user-123"
        assert domain_ticket.reporter_id == "user-456"
        assert domain_ticket.project_id == "project-789"
        assert domain_ticket.created_at == ticket_orm.created_at
        assert domain_ticket.updated_at == ticket_orm.updated_at

    def test_orm_to_domain_ticket_with_null_optional_fields(self, test_session: Session) -> None:
        """Test converting ticket ORM with null optional fields."""
        ticket_orm = TicketORM(
            title="Minimal Ticket",
            description=None,
            status=TicketStatus.TODO.value,
            priority=None,
            assignee_id=None,
            reporter_id="user-456",
            project_id="project-789",
        )
        test_session.add(ticket_orm)
        test_session.commit()
        test_session.refresh(ticket_orm)

        domain_ticket = orm_ticket_to_domain_ticket(ticket_orm)

        assert domain_ticket.title == "Minimal Ticket"
        assert domain_ticket.description is None
        assert domain_ticket.priority is None
        assert domain_ticket.assignee_id is None
        assert domain_ticket.status == TicketStatus.TODO
        assert domain_ticket.reporter_id == "user-456"
