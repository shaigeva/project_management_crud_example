"""Tests for Epic repository operations.

Tests verify complete CRUD functionality for epics through the Repository interface,
including organization scoping, data persistence, and edge cases.
"""

from datetime import datetime

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import (
    EpicCreateCommand,
    EpicData,
    EpicUpdateCommand,
)
from tests.conftest import test_repo  # noqa: F401
from tests.dal.helpers import create_test_epic_via_repo, create_test_org_via_repo


class TestEpicRepositoryCreate:
    """Test epic creation through repository."""

    def test_create_epic_with_all_fields(self, test_repo: Repository) -> None:
        """Test creating an epic with all fields through repository."""
        # Create organization first
        org = create_test_org_via_repo(test_repo)

        # Create epic
        epic_data = EpicData(name="Launch V1", description="MVP launch epic")
        command = EpicCreateCommand(epic_data=epic_data, organization_id=org.id)

        epic = test_repo.epics.create(command)

        assert epic.id is not None
        assert epic.name == "Launch V1"
        assert epic.description == "MVP launch epic"
        assert epic.organization_id == org.id
        assert isinstance(epic.created_at, datetime)
        assert isinstance(epic.updated_at, datetime)

    def test_create_epic_without_description(self, test_repo: Repository) -> None:
        """Test creating an epic without optional description."""
        # Create organization
        org = create_test_org_via_repo(test_repo)

        # Create epic without description
        epic_data = EpicData(name="Q1 Goals")
        command = EpicCreateCommand(epic_data=epic_data, organization_id=org.id)

        epic = test_repo.epics.create(command)

        assert epic.name == "Q1 Goals"
        assert epic.description is None
        assert epic.organization_id == org.id

    def test_create_epic_persists_to_database(self, test_repo: Repository) -> None:
        """Test that created epic can be retrieved from database."""
        # Create organization
        org = create_test_org_via_repo(test_repo)

        # Create epic
        epic_data = EpicData(name="Security Improvements")
        command = EpicCreateCommand(epic_data=epic_data, organization_id=org.id)
        created_epic = test_repo.epics.create(command)

        # Retrieve epic
        retrieved_epic = test_repo.epics.get_by_id(created_epic.id)

        assert retrieved_epic is not None
        assert retrieved_epic.id == created_epic.id
        assert retrieved_epic.name == created_epic.name
        assert retrieved_epic.organization_id == org.id


class TestEpicRepositoryGet:
    """Test epic retrieval operations."""

    def test_get_epic_by_id_found(self, test_repo: Repository) -> None:
        """Test retrieving an existing epic by ID."""
        # Create organization and epic
        org = create_test_org_via_repo(test_repo)
        epic = create_test_epic_via_repo(test_repo, org.id)

        # Retrieve epic
        retrieved = test_repo.epics.get_by_id(epic.id)

        assert retrieved is not None
        assert retrieved.id == epic.id
        assert retrieved.name == "Test Epic"

    def test_get_epic_by_id_not_found(self, test_repo: Repository) -> None:
        """Test retrieving a non-existent epic returns None."""
        result = test_repo.epics.get_by_id("non-existent-id")

        assert result is None

    def test_get_epics_by_organization_id(self, test_repo: Repository) -> None:
        """Test retrieving all epics for a specific organization."""
        # Create two organizations
        org1 = create_test_org_via_repo(test_repo, "Org 1")
        org2 = create_test_org_via_repo(test_repo, "Org 2")

        # Create epics for org1
        create_test_epic_via_repo(test_repo, org1.id, "Org1 Epic 1")
        create_test_epic_via_repo(test_repo, org1.id, "Org1 Epic 2")

        # Create epic for org2
        create_test_epic_via_repo(test_repo, org2.id, "Org2 Epic 1")

        # Get epics for org1
        org1_epics = test_repo.epics.get_by_organization_id(org1.id)

        assert len(org1_epics) == 2
        assert all(e.organization_id == org1.id for e in org1_epics)
        assert {e.name for e in org1_epics} == {"Org1 Epic 1", "Org1 Epic 2"}

    def test_get_all_epics(self, test_repo: Repository) -> None:
        """Test retrieving all epics across all organizations."""
        # Create two organizations
        org1 = create_test_org_via_repo(test_repo, "Org 1")
        org2 = create_test_org_via_repo(test_repo, "Org 2")

        # Create epics
        create_test_epic_via_repo(test_repo, org1.id, "Epic 1")
        create_test_epic_via_repo(test_repo, org2.id, "Epic 2")

        # Get all epics
        all_epics = test_repo.epics.get_all()

        assert len(all_epics) == 2
        assert {e.name for e in all_epics} == {"Epic 1", "Epic 2"}


class TestEpicRepositoryUpdate:
    """Test epic update operations."""

    def test_update_epic_name(self, test_repo: Repository) -> None:
        """Test updating epic name."""
        # Create organization and epic
        org = create_test_org_via_repo(test_repo)
        epic = create_test_epic_via_repo(test_repo, org.id, "Old Name")

        # Update name
        update_command = EpicUpdateCommand(name="New Name")
        updated_epic = test_repo.epics.update(epic.id, update_command)

        assert updated_epic is not None
        assert updated_epic.name == "New Name"
        assert updated_epic.description == epic.description  # Unchanged

    def test_update_epic_description(self, test_repo: Repository) -> None:
        """Test updating epic description."""
        # Create organization and epic
        org = create_test_org_via_repo(test_repo)
        epic = create_test_epic_via_repo(test_repo, org.id, "Epic", "Old description")

        # Update description
        update_command = EpicUpdateCommand(description="New description")
        updated_epic = test_repo.epics.update(epic.id, update_command)

        assert updated_epic is not None
        assert updated_epic.description == "New description"
        assert updated_epic.name == epic.name  # Unchanged

    def test_update_epic_all_fields(self, test_repo: Repository) -> None:
        """Test updating all epic fields."""
        # Create organization and epic
        org = create_test_org_via_repo(test_repo)
        epic = create_test_epic_via_repo(test_repo, org.id, "Old Name", "Old description")

        # Update all fields
        update_command = EpicUpdateCommand(name="New Name", description="New description")
        updated_epic = test_repo.epics.update(epic.id, update_command)

        assert updated_epic is not None
        assert updated_epic.name == "New Name"
        assert updated_epic.description == "New description"

    def test_update_epic_not_found(self, test_repo: Repository) -> None:
        """Test updating non-existent epic returns None."""
        update_command = EpicUpdateCommand(name="New Name")
        result = test_repo.epics.update("non-existent-id", update_command)

        assert result is None

    def test_update_epic_with_empty_command(self, test_repo: Repository) -> None:
        """Test updating epic with no fields succeeds (no-op)."""
        # Create organization and epic
        org = create_test_org_via_repo(test_repo)
        epic = create_test_epic_via_repo(test_repo, org.id, "Epic")

        # Update with empty command
        update_command = EpicUpdateCommand()
        updated_epic = test_repo.epics.update(epic.id, update_command)

        assert updated_epic is not None
        assert updated_epic.name == epic.name
        assert updated_epic.description == epic.description


class TestEpicRepositoryDelete:
    """Test epic deletion operations."""

    def test_delete_epic_succeeds(self, test_repo: Repository) -> None:
        """Test deleting an existing epic."""
        # Create organization and epic
        org = create_test_org_via_repo(test_repo)
        epic = create_test_epic_via_repo(test_repo, org.id, "To Delete")

        # Delete epic
        result = test_repo.epics.delete(epic.id)

        assert result is True

        # Verify deletion
        deleted_epic = test_repo.epics.get_by_id(epic.id)
        assert deleted_epic is None

    def test_delete_epic_not_found(self, test_repo: Repository) -> None:
        """Test deleting non-existent epic returns False."""
        result = test_repo.epics.delete("non-existent-id")

        assert result is False


class TestEpicRepositoryTimestamps:
    """Test epic timestamp behavior."""

    def test_created_at_and_updated_at_are_set_on_create(self, test_repo: Repository) -> None:
        """Test that both timestamps are set when creating an epic."""
        # Create organization and epic
        org = create_test_org_via_repo(test_repo)
        epic = create_test_epic_via_repo(test_repo, org.id)

        assert isinstance(epic.created_at, datetime)
        assert isinstance(epic.updated_at, datetime)

        # Initially, created_at and updated_at should be very close
        time_diff = abs((epic.updated_at - epic.created_at).total_seconds())
        assert time_diff < 1.0  # Less than 1 second difference


class TestEpicRepositoryWorkflows:
    """Test complete epic workflows."""

    def test_complete_epic_workflow(self, test_repo: Repository) -> None:
        """Test complete workflow: create, read, update, list, delete."""
        # 1. Create organization
        org = create_test_org_via_repo(test_repo, "Workflow Org")

        # 2. Create epic
        epic_data = EpicData(name="Workflow Epic", description="Initial description")
        create_command = EpicCreateCommand(epic_data=epic_data, organization_id=org.id)
        created_epic = test_repo.epics.create(create_command)

        assert created_epic.name == "Workflow Epic"
        assert created_epic.organization_id == org.id

        # 3. Read epic
        retrieved_epic = test_repo.epics.get_by_id(created_epic.id)
        assert retrieved_epic is not None
        assert retrieved_epic.name == "Workflow Epic"

        # 4. Update epic
        update_command = EpicUpdateCommand(name="Updated Epic", description="Updated description")
        updated_epic = test_repo.epics.update(created_epic.id, update_command)
        assert updated_epic is not None
        assert updated_epic.name == "Updated Epic"

        # 5. List epics for organization
        org_epics = test_repo.epics.get_by_organization_id(org.id)
        assert len(org_epics) == 1
        assert org_epics[0].name == "Updated Epic"

        # 6. Delete epic
        delete_result = test_repo.epics.delete(created_epic.id)
        assert delete_result is True

        # 7. Verify deletion
        deleted_epic = test_repo.epics.get_by_id(created_epic.id)
        assert deleted_epic is None

    def test_multiple_epics_in_same_organization(self, test_repo: Repository) -> None:
        """Test creating multiple epics within the same organization."""
        # Create organization
        org = create_test_org_via_repo(test_repo, "Multi-Epic Org")

        # Create multiple epics
        create_test_epic_via_repo(test_repo, org.id, "Backend")
        create_test_epic_via_repo(test_repo, org.id, "Frontend")
        create_test_epic_via_repo(test_repo, org.id, "Mobile")

        # List all epics for organization
        org_epics = test_repo.epics.get_by_organization_id(org.id)

        assert len(org_epics) == 3
        assert {e.name for e in org_epics} == {"Backend", "Frontend", "Mobile"}
        assert all(e.organization_id == org.id for e in org_epics)

    def test_epics_isolated_by_organization(self, test_repo: Repository) -> None:
        """Test that epics are properly isolated by organization."""
        # Create two organizations
        org1 = create_test_org_via_repo(test_repo, "Org 1")
        org2 = create_test_org_via_repo(test_repo, "Org 2")

        # Create epics for each organization
        create_test_epic_via_repo(test_repo, org1.id, "Org1 Backend")
        create_test_epic_via_repo(test_repo, org1.id, "Org1 Frontend")
        create_test_epic_via_repo(test_repo, org2.id, "Org2 Mobile")

        # Get epics for each organization
        org1_epics = test_repo.epics.get_by_organization_id(org1.id)
        org2_epics = test_repo.epics.get_by_organization_id(org2.id)

        # Verify isolation
        assert len(org1_epics) == 2
        assert len(org2_epics) == 1
        assert all(e.organization_id == org1.id for e in org1_epics)
        assert all(e.organization_id == org2.id for e in org2_epics)
        assert {e.name for e in org1_epics} == {"Org1 Backend", "Org1 Frontend"}
        assert {e.name for e in org2_epics} == {"Org2 Mobile"}
