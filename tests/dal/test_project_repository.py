"""Tests for Project repository operations.

Tests verify complete CRUD functionality for projects through the Repository interface,
including organization scoping, data persistence, and edge cases.
"""

from datetime import datetime

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import (
    ProjectCreateCommand,
    ProjectData,
    ProjectUpdateCommand,
)
from tests.conftest import test_repo  # noqa: F401
from tests.dal.helpers import create_test_org_via_repo, create_test_project_via_repo


class TestProjectRepositoryCreate:
    """Test project creation through repository."""

    def test_create_project_with_all_fields(self, test_repo: Repository) -> None:
        """Test creating a project with all fields through repository."""
        # Create organization first
        org = create_test_org_via_repo(test_repo)

        # Create project
        project_data = ProjectData(name="Backend API", description="REST API for the application")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org.id)

        project = test_repo.projects.create(command)

        assert project.id is not None
        assert project.name == "Backend API"
        assert project.description == "REST API for the application"
        assert project.organization_id == org.id
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)

    def test_create_project_without_description(self, test_repo: Repository) -> None:
        """Test creating a project without optional description."""
        # Create organization
        org = create_test_org_via_repo(test_repo)

        # Create project without description
        project_data = ProjectData(name="Frontend")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org.id)

        project = test_repo.projects.create(command)

        assert project.name == "Frontend"
        assert project.description is None
        assert project.organization_id == org.id

    def test_create_project_persists_to_database(self, test_repo: Repository) -> None:
        """Test that created project can be retrieved from database."""
        # Create organization
        org = create_test_org_via_repo(test_repo)

        # Create project
        project_data = ProjectData(name="Mobile App")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org.id)
        created_project = test_repo.projects.create(command)

        # Retrieve project
        retrieved_project = test_repo.projects.get_by_id(created_project.id)

        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        assert retrieved_project.name == created_project.name
        assert retrieved_project.organization_id == org.id


class TestProjectRepositoryGet:
    """Test project retrieval operations."""

    def test_get_project_by_id_found(self, test_repo: Repository) -> None:
        """Test retrieving an existing project by ID."""
        # Create organization and project
        org = create_test_org_via_repo(test_repo)
        project = create_test_project_via_repo(test_repo, org.id)

        # Retrieve project
        retrieved = test_repo.projects.get_by_id(project.id)

        assert retrieved is not None
        assert retrieved.id == project.id
        assert retrieved.name == "Test Project"

    def test_get_project_by_id_not_found(self, test_repo: Repository) -> None:
        """Test retrieving a non-existent project returns None."""
        result = test_repo.projects.get_by_id("non-existent-id")

        assert result is None

    def test_get_projects_by_organization_id(self, test_repo: Repository) -> None:
        """Test retrieving all projects for a specific organization."""
        # Create two organizations
        org1 = create_test_org_via_repo(test_repo, "Org 1")
        org2 = create_test_org_via_repo(test_repo, "Org 2")

        # Create projects for org1
        create_test_project_via_repo(test_repo, org1.id, "Org1 Project 1")
        create_test_project_via_repo(test_repo, org1.id, "Org1 Project 2")

        # Create project for org2
        create_test_project_via_repo(test_repo, org2.id, "Org2 Project 1")

        # Get projects for org1
        org1_projects = test_repo.projects.get_by_organization_id(org1.id)

        assert len(org1_projects) == 2
        assert all(p.organization_id == org1.id for p in org1_projects)
        assert {p.name for p in org1_projects} == {"Org1 Project 1", "Org1 Project 2"}

    def test_get_all_projects(self, test_repo: Repository) -> None:
        """Test retrieving all projects across all organizations."""
        # Create two organizations
        org1 = create_test_org_via_repo(test_repo, "Org 1")
        org2 = create_test_org_via_repo(test_repo, "Org 2")

        # Create projects
        create_test_project_via_repo(test_repo, org1.id, "Project 1")
        create_test_project_via_repo(test_repo, org2.id, "Project 2")

        # Get all projects
        all_projects = test_repo.projects.get_all()

        assert len(all_projects) == 2
        assert {p.name for p in all_projects} == {"Project 1", "Project 2"}


class TestProjectRepositoryUpdate:
    """Test project update operations."""

    def test_update_project_name(self, test_repo: Repository) -> None:
        """Test updating project name."""
        # Create organization and project
        org = create_test_org_via_repo(test_repo)
        project = create_test_project_via_repo(test_repo, org.id, "Old Name")

        # Update name
        update_command = ProjectUpdateCommand(name="New Name")
        updated_project = test_repo.projects.update(project.id, update_command)

        assert updated_project is not None
        assert updated_project.name == "New Name"
        assert updated_project.description == project.description  # Unchanged

    def test_update_project_description(self, test_repo: Repository) -> None:
        """Test updating project description."""
        # Create organization and project
        org = create_test_org_via_repo(test_repo)
        project = create_test_project_via_repo(test_repo, org.id, "Project", "Old description")

        # Update description
        update_command = ProjectUpdateCommand(description="New description")
        updated_project = test_repo.projects.update(project.id, update_command)

        assert updated_project is not None
        assert updated_project.description == "New description"
        assert updated_project.name == project.name  # Unchanged

    def test_update_project_all_fields(self, test_repo: Repository) -> None:
        """Test updating all project fields."""
        # Create organization and project
        org = create_test_org_via_repo(test_repo)
        project = create_test_project_via_repo(test_repo, org.id, "Old Name", "Old description")

        # Update all fields
        update_command = ProjectUpdateCommand(name="New Name", description="New description")
        updated_project = test_repo.projects.update(project.id, update_command)

        assert updated_project is not None
        assert updated_project.name == "New Name"
        assert updated_project.description == "New description"

    def test_update_project_not_found(self, test_repo: Repository) -> None:
        """Test updating non-existent project returns None."""
        update_command = ProjectUpdateCommand(name="New Name")
        result = test_repo.projects.update("non-existent-id", update_command)

        assert result is None

    def test_update_project_with_empty_command(self, test_repo: Repository) -> None:
        """Test updating project with no fields succeeds (no-op)."""
        # Create organization and project
        org = create_test_org_via_repo(test_repo)
        project = create_test_project_via_repo(test_repo, org.id, "Project")

        # Update with empty command
        update_command = ProjectUpdateCommand()
        updated_project = test_repo.projects.update(project.id, update_command)

        assert updated_project is not None
        assert updated_project.name == project.name
        assert updated_project.description == project.description


class TestProjectRepositoryDelete:
    """Test project deletion operations."""

    def test_delete_project_succeeds(self, test_repo: Repository) -> None:
        """Test deleting an existing project."""
        # Create organization and project
        org = create_test_org_via_repo(test_repo)
        project = create_test_project_via_repo(test_repo, org.id, "To Delete")

        # Delete project
        result = test_repo.projects.delete(project.id)

        assert result is True

        # Verify deletion
        deleted_project = test_repo.projects.get_by_id(project.id)
        assert deleted_project is None

    def test_delete_project_not_found(self, test_repo: Repository) -> None:
        """Test deleting non-existent project returns False."""
        result = test_repo.projects.delete("non-existent-id")

        assert result is False


class TestProjectRepositoryTimestamps:
    """Test project timestamp behavior."""

    def test_created_at_and_updated_at_are_set_on_create(self, test_repo: Repository) -> None:
        """Test that both timestamps are set when creating a project."""
        # Create organization and project
        org = create_test_org_via_repo(test_repo)
        project = create_test_project_via_repo(test_repo, org.id)

        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)

        # Initially, created_at and updated_at should be very close
        time_diff = abs((project.updated_at - project.created_at).total_seconds())
        assert time_diff < 1.0  # Less than 1 second difference


class TestProjectRepositoryWorkflows:
    """Test complete project workflows."""

    def test_complete_project_workflow(self, test_repo: Repository) -> None:
        """Test complete workflow: create, read, update, list, delete."""
        # 1. Create organization
        org = create_test_org_via_repo(test_repo, "Workflow Org")

        # 2. Create project
        project_data = ProjectData(name="Workflow Project", description="Initial description")
        create_command = ProjectCreateCommand(project_data=project_data, organization_id=org.id)
        created_project = test_repo.projects.create(create_command)

        assert created_project.name == "Workflow Project"
        assert created_project.organization_id == org.id

        # 3. Read project
        retrieved_project = test_repo.projects.get_by_id(created_project.id)
        assert retrieved_project is not None
        assert retrieved_project.name == "Workflow Project"

        # 4. Update project
        update_command = ProjectUpdateCommand(name="Updated Project", description="Updated description")
        updated_project = test_repo.projects.update(created_project.id, update_command)
        assert updated_project is not None
        assert updated_project.name == "Updated Project"

        # 5. List projects for organization
        org_projects = test_repo.projects.get_by_organization_id(org.id)
        assert len(org_projects) == 1
        assert org_projects[0].name == "Updated Project"

        # 6. Delete project
        delete_result = test_repo.projects.delete(created_project.id)
        assert delete_result is True

        # 7. Verify deletion
        deleted_project = test_repo.projects.get_by_id(created_project.id)
        assert deleted_project is None

    def test_multiple_projects_in_same_organization(self, test_repo: Repository) -> None:
        """Test creating multiple projects within the same organization."""
        # Create organization
        org = create_test_org_via_repo(test_repo, "Multi-Project Org")

        # Create multiple projects
        create_test_project_via_repo(test_repo, org.id, "Backend")
        create_test_project_via_repo(test_repo, org.id, "Frontend")
        create_test_project_via_repo(test_repo, org.id, "Mobile")

        # List all projects for organization
        org_projects = test_repo.projects.get_by_organization_id(org.id)

        assert len(org_projects) == 3
        assert {p.name for p in org_projects} == {"Backend", "Frontend", "Mobile"}
        assert all(p.organization_id == org.id for p in org_projects)

    def test_projects_isolated_by_organization(self, test_repo: Repository) -> None:
        """Test that projects are properly isolated by organization."""
        # Create two organizations
        org1 = create_test_org_via_repo(test_repo, "Org 1")
        org2 = create_test_org_via_repo(test_repo, "Org 2")

        # Create projects for each organization
        create_test_project_via_repo(test_repo, org1.id, "Org1 Backend")
        create_test_project_via_repo(test_repo, org1.id, "Org1 Frontend")
        create_test_project_via_repo(test_repo, org2.id, "Org2 Mobile")

        # Get projects for each organization
        org1_projects = test_repo.projects.get_by_organization_id(org1.id)
        org2_projects = test_repo.projects.get_by_organization_id(org2.id)

        # Verify isolation
        assert len(org1_projects) == 2
        assert len(org2_projects) == 1
        assert all(p.organization_id == org1.id for p in org1_projects)
        assert all(p.organization_id == org2.id for p in org2_projects)
        assert {p.name for p in org1_projects} == {"Org1 Backend", "Org1 Frontend"}
        assert {p.name for p in org2_projects} == {"Org2 Mobile"}
