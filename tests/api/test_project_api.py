"""Tests for project API endpoints."""

import pytest
from fastapi.testclient import TestClient

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import (
    OrganizationCreateCommand,
    OrganizationData,
    ProjectCreateCommand,
    ProjectData,
    UserCreateCommand,
    UserData,
    UserRole,
)
from tests.conftest import client, test_repo  # noqa: F401


@pytest.fixture
def organization(test_repo: Repository) -> str:
    """Create a test organization and return its ID."""
    org_data = OrganizationData(name="Test Organization", description="Test org for projects")
    org_command = OrganizationCreateCommand(organization_data=org_data)
    org = test_repo.organizations.create(org_command)
    return org.id


@pytest.fixture
def second_organization(test_repo: Repository) -> str:
    """Create a second organization for cross-org tests."""
    org_data = OrganizationData(name="Second Organization", description="Another org")
    org_command = OrganizationCreateCommand(organization_data=org_data)
    org = test_repo.organizations.create(org_command)
    return org.id


@pytest.fixture
def super_admin_token(test_repo: Repository, client: TestClient) -> str:
    """Create Super Admin and return auth token."""
    user_data = UserData(
        username="superadmin",
        email="superadmin@example.com",
        full_name="Super Admin",
    )
    password = "SuperAdminPass123"
    command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id=None,
        role=UserRole.SUPER_ADMIN,
    )
    test_repo.users.create(command)

    response = client.post("/auth/login", json={"username": "superadmin", "password": password})
    return response.json()["access_token"]


@pytest.fixture
def admin_token(test_repo: Repository, client: TestClient, organization: str) -> tuple[str, str]:
    """Create Admin user and return token and org_id."""
    user_data = UserData(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
    )
    password = "AdminPass123"
    command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id=organization,
        role=UserRole.ADMIN,
    )
    test_repo.users.create(command)

    response = client.post("/auth/login", json={"username": "admin", "password": password})
    return response.json()["access_token"], organization


@pytest.fixture
def project_manager_token(test_repo: Repository, client: TestClient, organization: str) -> tuple[str, str]:
    """Create Project Manager user and return token and org_id."""
    user_data = UserData(
        username="projectmanager",
        email="pm@example.com",
        full_name="Project Manager",
    )
    password = "PMPass123"
    command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id=organization,
        role=UserRole.PROJECT_MANAGER,
    )
    test_repo.users.create(command)

    response = client.post("/auth/login", json={"username": "projectmanager", "password": password})
    return response.json()["access_token"], organization


@pytest.fixture
def write_user_token(test_repo: Repository, client: TestClient, organization: str) -> tuple[str, str]:
    """Create Write Access user and return token and org_id."""
    user_data = UserData(
        username="writer",
        email="writer@example.com",
        full_name="Write User",
    )
    password = "WriterPass123"
    command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id=organization,
        role=UserRole.WRITE_ACCESS,
    )
    test_repo.users.create(command)

    response = client.post("/auth/login", json={"username": "writer", "password": password})
    return response.json()["access_token"], organization


@pytest.fixture
def read_user_token(test_repo: Repository, client: TestClient, organization: str) -> tuple[str, str]:
    """Create Read Access user and return token and org_id."""
    user_data = UserData(
        username="reader",
        email="reader@example.com",
        full_name="Read User",
    )
    password = "ReaderPass123"
    command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id=organization,
        role=UserRole.READ_ACCESS,
    )
    test_repo.users.create(command)

    response = client.post("/auth/login", json={"username": "reader", "password": password})
    return response.json()["access_token"], organization


class TestCreateProject:
    """Tests for POST /api/projects endpoint."""

    def test_create_project_as_admin(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test creating project as Admin."""
        token, org_id = admin_token
        project_data = {"name": "Backend Project", "description": "Backend development"}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Backend Project"
        assert data["description"] == "Backend development"
        assert data["organization_id"] == org_id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_project_as_project_manager(
        self, client: TestClient, project_manager_token: tuple[str, str]
    ) -> None:
        """Test creating project as Project Manager."""
        token, org_id = project_manager_token
        project_data = {"name": "Frontend Project"}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Frontend Project"
        assert data["description"] is None
        assert data["organization_id"] == org_id

    def test_create_project_without_description(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test creating project with only name."""
        token, _ = admin_token
        project_data = {"name": "Minimal Project"}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"
        assert data["description"] is None

    def test_create_project_as_write_user_fails(self, client: TestClient, write_user_token: tuple[str, str]) -> None:
        """Test that Write Access user cannot create projects."""
        token, _ = write_user_token
        project_data = {"name": "Unauthorized Project"}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_create_project_as_read_user_fails(self, client: TestClient, read_user_token: tuple[str, str]) -> None:
        """Test that Read Access user cannot create projects."""
        token, _ = read_user_token
        project_data = {"name": "Unauthorized Project"}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_create_project_without_auth_fails(self, client: TestClient) -> None:
        """Test that creating project without auth fails."""
        project_data = {"name": "No Auth Project"}

        response = client.post("/api/projects", json=project_data)

        assert response.status_code == 401

    def test_create_project_with_special_characters(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test creating project with special characters in name."""
        token, _ = admin_token
        project_data = {"name": "Special !@#$%^&*() Project"}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Special !@#$%^&*() Project"

    def test_create_project_with_unicode(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test creating project with Unicode characters."""
        token, _ = admin_token
        project_data = {"name": "Proyecto Español 日本"}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Proyecto Español 日本"

    def test_create_project_with_empty_name_fails(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test that creating project with empty name fails."""
        token, _ = admin_token
        project_data = {"name": ""}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    def test_create_project_with_long_name(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test creating project with maximum length name (255 chars)."""
        token, _ = admin_token
        long_name = "A" * 255
        project_data = {"name": long_name}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert response.json()["name"] == long_name

    def test_create_project_with_too_long_name_fails(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test that creating project with name >255 chars fails."""
        token, _ = admin_token
        too_long_name = "A" * 256
        project_data = {"name": too_long_name}

        response = client.post(
            "/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


class TestGetProject:
    """Tests for GET /api/projects/{id} endpoint."""

    def test_get_project_by_id_in_same_org(
        self, client: TestClient, admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test getting project by ID as user in same organization."""
        token, org_id = admin_token

        # Create a project
        project_data = ProjectData(name="Test Project", description="Test description")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
        project = test_repo.projects.create(command)

        response = client.get(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == "Test Project"
        assert data["description"] == "Test description"
        assert data["organization_id"] == org_id

    def test_get_project_from_different_org_fails(
        self,
        client: TestClient,
        admin_token: tuple[str, str],
        second_organization: str,
        test_repo: Repository,
    ) -> None:
        """Test that user cannot get project from different organization."""
        token, _ = admin_token

        # Create project in different organization
        project_data = ProjectData(name="Other Org Project")
        command = ProjectCreateCommand(project_data=project_data, organization_id=second_organization)
        project = test_repo.projects.create(command)

        response = client.get(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "different organization" in response.json()["detail"]

    def test_get_project_as_super_admin_from_any_org(
        self,
        client: TestClient,
        super_admin_token: str,
        organization: str,
        test_repo: Repository,
    ) -> None:
        """Test that Super Admin can get project from any organization."""
        # Create project in organization
        project_data = ProjectData(name="Any Org Project")
        command = ProjectCreateCommand(project_data=project_data, organization_id=organization)
        project = test_repo.projects.create(command)

        response = client.get(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {super_admin_token}"},
        )

        assert response.status_code == 200
        assert response.json()["id"] == project.id

    def test_get_nonexistent_project_returns_404(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test getting non-existent project returns 404."""
        token, _ = admin_token

        response = client.get(
            "/api/projects/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_project_without_auth_fails(self, client: TestClient, test_repo: Repository, organization: str) -> None:
        """Test getting project without auth fails."""
        # Create a project
        project_data = ProjectData(name="Test Project")
        command = ProjectCreateCommand(project_data=project_data, organization_id=organization)
        project = test_repo.projects.create(command)

        response = client.get(f"/api/projects/{project.id}")

        assert response.status_code == 401


class TestListProjects:
    """Tests for GET /api/projects endpoint."""

    def test_list_projects_in_own_org(
        self, client: TestClient, admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test listing projects as user sees only their org's projects."""
        token, org_id = admin_token

        # Create projects in user's organization
        for i in range(3):
            project_data = ProjectData(name=f"Project {i}")
            command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
            test_repo.projects.create(command)

        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 3
        assert all(p["organization_id"] == org_id for p in projects)

    def test_list_projects_does_not_include_other_orgs(
        self,
        client: TestClient,
        admin_token: tuple[str, str],
        second_organization: str,
        test_repo: Repository,
    ) -> None:
        """Test that listing projects does not include projects from other organizations."""
        token, org_id = admin_token

        # Create project in user's org
        project_data1 = ProjectData(name="My Project")
        command1 = ProjectCreateCommand(project_data=project_data1, organization_id=org_id)
        test_repo.projects.create(command1)

        # Create project in different org
        project_data2 = ProjectData(name="Other Project")
        command2 = ProjectCreateCommand(project_data=project_data2, organization_id=second_organization)
        test_repo.projects.create(command2)

        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["name"] == "My Project"
        assert projects[0]["organization_id"] == org_id

    def test_list_projects_as_super_admin_sees_all(
        self,
        client: TestClient,
        super_admin_token: str,
        organization: str,
        second_organization: str,
        test_repo: Repository,
    ) -> None:
        """Test that Super Admin sees projects from all organizations."""
        # Create projects in different orgs
        project_data1 = ProjectData(name="Org1 Project")
        command1 = ProjectCreateCommand(project_data=project_data1, organization_id=organization)
        test_repo.projects.create(command1)

        project_data2 = ProjectData(name="Org2 Project")
        command2 = ProjectCreateCommand(project_data=project_data2, organization_id=second_organization)
        test_repo.projects.create(command2)

        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {super_admin_token}"},
        )

        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 2
        org_ids = {p["organization_id"] for p in projects}
        assert org_ids == {organization, second_organization}

    def test_list_projects_when_empty(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test listing projects when none exist returns empty array."""
        token, _ = admin_token

        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_list_projects_without_auth_fails(self, client: TestClient) -> None:
        """Test listing projects without auth fails."""
        response = client.get("/api/projects")

        assert response.status_code == 401


class TestUpdateProject:
    """Tests for PUT /api/projects/{id} endpoint."""

    def test_update_project_as_admin(
        self, client: TestClient, admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test updating project as Admin."""
        token, org_id = admin_token

        # Create project
        project_data = ProjectData(name="Original Name", description="Original description")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
        project = test_repo.projects.create(command)

        # Update project
        update_data = {"name": "Updated Name", "description": "Updated description"}
        response = client.put(
            f"/api/projects/{project.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["id"] == project.id

    def test_update_project_as_project_manager(
        self, client: TestClient, project_manager_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test updating project as Project Manager."""
        token, org_id = project_manager_token

        # Create project
        project_data = ProjectData(name="Original Name")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
        project = test_repo.projects.create(command)

        # Update project
        update_data = {"name": "PM Updated Name"}
        response = client.put(
            f"/api/projects/{project.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "PM Updated Name"

    def test_update_project_partial_update(
        self, client: TestClient, admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test partial update of project (only name or description)."""
        token, org_id = admin_token

        # Create project
        project_data = ProjectData(name="Original", description="Original description")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
        project = test_repo.projects.create(command)

        # Update only name
        update_data = {"name": "New Name"}
        response = client.put(
            f"/api/projects/{project.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "Original description"  # Unchanged

    def test_update_project_from_different_org_fails(
        self,
        client: TestClient,
        admin_token: tuple[str, str],
        second_organization: str,
        test_repo: Repository,
    ) -> None:
        """Test that user cannot update project from different organization."""
        token, _ = admin_token

        # Create project in different org
        project_data = ProjectData(name="Other Org Project")
        command = ProjectCreateCommand(project_data=project_data, organization_id=second_organization)
        project = test_repo.projects.create(command)

        # Attempt to update
        update_data = {"name": "Hacked Name"}
        response = client.put(
            f"/api/projects/{project.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "different organization" in response.json()["detail"]

    def test_update_project_as_write_user_fails(
        self, client: TestClient, write_user_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test that Write Access user cannot update projects."""
        token, org_id = write_user_token

        # Create project
        project_data = ProjectData(name="Project")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
        project = test_repo.projects.create(command)

        # Attempt to update
        update_data = {"name": "Unauthorized Update"}
        response = client.put(
            f"/api/projects/{project.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_update_nonexistent_project_returns_404(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test updating non-existent project returns 404."""
        token, _ = admin_token

        update_data = {"name": "New Name"}
        response = client.put(
            "/api/projects/nonexistent-id",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


class TestDeleteProject:
    """Tests for DELETE /api/projects/{id} endpoint."""

    def test_delete_project_as_admin(
        self, client: TestClient, admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test deleting project as Admin."""
        token, org_id = admin_token

        # Create project
        project_data = ProjectData(name="To Delete")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
        project = test_repo.projects.create(command)

        # Delete project
        response = client.delete(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify project is deleted
        get_response = client.get(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == 404

    def test_delete_project_as_project_manager_fails(
        self, client: TestClient, project_manager_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test that Project Manager cannot delete projects."""
        token, org_id = project_manager_token

        # Create project
        project_data = ProjectData(name="Protected Project")
        command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
        project = test_repo.projects.create(command)

        # Attempt to delete
        response = client.delete(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_delete_project_from_different_org_fails(
        self,
        client: TestClient,
        admin_token: tuple[str, str],
        second_organization: str,
        test_repo: Repository,
    ) -> None:
        """Test that Admin cannot delete project from different organization."""
        token, _ = admin_token

        # Create project in different org
        project_data = ProjectData(name="Other Org Project")
        command = ProjectCreateCommand(project_data=project_data, organization_id=second_organization)
        project = test_repo.projects.create(command)

        # Attempt to delete
        response = client.delete(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "different organization" in response.json()["detail"]

    def test_delete_project_as_super_admin_from_any_org(
        self,
        client: TestClient,
        super_admin_token: str,
        organization: str,
        test_repo: Repository,
    ) -> None:
        """Test that Super Admin can delete project from any organization."""
        # Create project
        project_data = ProjectData(name="To Delete")
        command = ProjectCreateCommand(project_data=project_data, organization_id=organization)
        project = test_repo.projects.create(command)

        # Delete as Super Admin
        response = client.delete(
            f"/api/projects/{project.id}",
            headers={"Authorization": f"Bearer {super_admin_token}"},
        )

        assert response.status_code == 204

    def test_delete_nonexistent_project_returns_404(self, client: TestClient, admin_token: tuple[str, str]) -> None:
        """Test deleting non-existent project returns 404."""
        token, _ = admin_token

        response = client.delete(
            "/api/projects/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


class TestProjectWorkflows:
    """Test complete project workflows."""

    def test_complete_project_crud_workflow(
        self, client: TestClient, admin_token: tuple[str, str], test_repo: Repository
    ) -> None:
        """Test complete CRUD workflow for a project."""
        token, org_id = admin_token

        # 1. Create project
        create_data = {"name": "Workflow Project", "description": "Full CRUD test"}
        create_response = client.post(
            "/api/projects",
            json=create_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # 2. Get project
        get_response = client.get(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Workflow Project"

        # 3. Update project
        update_response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "Updated Workflow", "description": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Workflow"

        # 4. List projects includes updated project
        list_response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.status_code == 200
        assert any(p["id"] == project_id for p in list_response.json())

        # 5. Delete project
        delete_response = client.delete(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_response.status_code == 204

        # 6. Verify deletion
        final_get = client.get(
            f"/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert final_get.status_code == 404
