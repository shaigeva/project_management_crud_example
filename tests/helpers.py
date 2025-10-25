"""Test helper functions for reducing repetition in tests.

This module provides simple helper functions to create common test data
and reduce boilerplate in test files.
"""

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


def auth_headers(token: str) -> dict[str, str]:
    """Create authorization headers from token.

    Args:
        token: Authentication token

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {token}"}


def create_test_org(test_repo: Repository, name: str = "Test Org", description: str | None = None) -> str:
    """Create a test organization and return its ID.

    Args:
        test_repo: Repository instance
        name: Organization name (default: "Test Org")
        description: Optional organization description (default: None)

    Returns:
        Organization ID
    """
    org = test_repo.organizations.create(
        OrganizationCreateCommand(organization_data=OrganizationData(name=name, description=description))
    )
    return org.id


def create_test_user(
    test_repo: Repository,
    org_id: str,
    username: str = "testuser",
    email: str | None = None,
    full_name: str | None = None,
    role: UserRole = UserRole.WRITE_ACCESS,
    password: str = "TestPass123",
) -> str:
    """Create a test user and return the user ID.

    Args:
        test_repo: Repository instance
        org_id: Organization ID for the user
        username: Username (default: "testuser")
        email: Email (default: {username}@example.com)
        full_name: Full name (default: capitalized username)
        role: User role (default: WRITE_ACCESS)
        password: Password (default: "TestPass123")

    Returns:
        User ID
    """
    email = email or f"{username}@example.com"
    full_name = full_name or username.replace("_", " ").title()
    user_data = UserData(username=username, email=email, full_name=full_name)
    command = UserCreateCommand(user_data=user_data, password=password, organization_id=org_id, role=role)
    user = test_repo.users.create(command)
    return user.id


def create_test_project_via_api(
    client: TestClient, token: str, name: str = "Test Project", description: str | None = None
) -> str:
    """Create a project via API and return its ID.

    Args:
        client: FastAPI TestClient
        token: Authentication token
        name: Project name (default: "Test Project")
        description: Optional project description (default: None)

    Returns:
        Project ID
    """
    headers = auth_headers(token)
    project_data = {"name": name}
    if description is not None:
        project_data["description"] = description
    response = client.post("/api/projects", json=project_data, headers=headers)
    return response.json()["id"]


def create_test_project_via_repo(
    test_repo: Repository, org_id: str, name: str = "Test Project", description: str | None = None
) -> str:
    """Create a project via repository and return its ID.

    Args:
        test_repo: Repository instance
        org_id: Organization ID for the project
        name: Project name (default: "Test Project")
        description: Optional project description (default: None)

    Returns:
        Project ID
    """
    project_data = ProjectData(name=name, description=description)
    command = ProjectCreateCommand(project_data=project_data, organization_id=org_id)
    project = test_repo.projects.create(command)
    return project.id
