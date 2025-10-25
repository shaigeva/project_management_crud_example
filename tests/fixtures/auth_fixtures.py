"""Authentication and user token fixtures for API tests.

This module provides centralized fixtures for creating users with various roles
and obtaining their authentication tokens.
"""

import pytest
from fastapi.testclient import TestClient

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import (
    OrganizationCreateCommand,
    OrganizationData,
    UserCreateCommand,
    UserData,
    UserRole,
)
from tests.conftest import client, test_repo  # noqa: F401


@pytest.fixture
def super_admin_token(test_repo: Repository, client: TestClient) -> str:
    """Create Super Admin user and return authentication token.

    Returns:
        JWT authentication token for Super Admin user
    """
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

    # Login to get token
    response = client.post("/auth/login", json={"username": "superadmin", "password": password})
    return response.json()["access_token"]


@pytest.fixture
def org_admin_token(test_repo: Repository, client: TestClient) -> tuple[str, str]:
    """Create organization and Org Admin user, return token and org_id.

    Returns:
        Tuple of (auth_token, organization_id)
    """
    # Create organization
    org_data = OrganizationData(name="Test Organization", description="Test org for admin")
    org_command = OrganizationCreateCommand(organization_data=org_data)
    org = test_repo.organizations.create(org_command)

    # Create admin user
    user_data = UserData(
        username="orgadmin",
        email="orgadmin@example.com",
        full_name="Org Admin",
    )
    password = "OrgAdminPass123"
    user_command = UserCreateCommand(
        user_data=user_data,
        password=password,
        organization_id=org.id,
        role=UserRole.ADMIN,
    )
    test_repo.users.create(user_command)

    # Login to get token
    response = client.post("/auth/login", json={"username": "orgadmin", "password": password})
    return response.json()["access_token"], org.id


@pytest.fixture
def project_manager_token(test_repo: Repository, client: TestClient) -> tuple[str, str]:
    """Create organization and Project Manager user, return token and org_id.

    Returns:
        Tuple of (auth_token, organization_id)
    """
    # Create organization
    org_data = OrganizationData(name="PM Organization", description="Org for project manager")
    org = test_repo.organizations.create(OrganizationCreateCommand(organization_data=org_data))

    # Create project manager user
    user_data = UserData(
        username="projectmanager",
        email="pm@example.com",
        full_name="Project Manager",
    )
    password = "PMPass123"
    test_repo.users.create(
        UserCreateCommand(
            user_data=user_data,
            password=password,
            organization_id=org.id,
            role=UserRole.PROJECT_MANAGER,
        )
    )

    # Login to get token
    response = client.post("/auth/login", json={"username": "projectmanager", "password": password})
    return response.json()["access_token"], org.id


@pytest.fixture
def write_user_token(test_repo: Repository, client: TestClient) -> tuple[str, str]:
    """Create organization and Write Access user, return token and org_id.

    Returns:
        Tuple of (auth_token, organization_id)
    """
    # Create organization
    org_data = OrganizationData(name="Writer Organization", description="Org for write user")
    org = test_repo.organizations.create(OrganizationCreateCommand(organization_data=org_data))

    # Create write access user
    user_data = UserData(
        username="writer",
        email="writer@example.com",
        full_name="Write User",
    )
    password = "WriterPass123"
    test_repo.users.create(
        UserCreateCommand(
            user_data=user_data,
            password=password,
            organization_id=org.id,
            role=UserRole.WRITE_ACCESS,
        )
    )

    # Login to get token
    response = client.post("/auth/login", json={"username": "writer", "password": password})
    return response.json()["access_token"], org.id


@pytest.fixture
def read_user_token(test_repo: Repository, client: TestClient) -> tuple[str, str]:
    """Create organization and Read Access user, return token and org_id.

    Returns:
        Tuple of (auth_token, organization_id)
    """
    # Create organization
    org_data = OrganizationData(name="Reader Organization", description="Org for read user")
    org = test_repo.organizations.create(OrganizationCreateCommand(organization_data=org_data))

    # Create read access user
    user_data = UserData(
        username="reader",
        email="reader@example.com",
        full_name="Read User",
    )
    password = "ReaderPass123"
    test_repo.users.create(
        UserCreateCommand(
            user_data=user_data,
            password=password,
            organization_id=org.id,
            role=UserRole.READ_ACCESS,
        )
    )

    # Login to get token
    response = client.post("/auth/login", json={"username": "reader", "password": password})
    return response.json()["access_token"], org.id
