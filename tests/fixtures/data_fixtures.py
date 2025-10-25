"""Test data fixtures for creating organizations, projects, and tickets.

This module provides centralized fixtures for creating test data entities
used across multiple test files.
"""

import pytest

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import OrganizationCreateCommand, OrganizationData
from tests.conftest import test_repo  # noqa: F401


@pytest.fixture
def organization(test_repo: Repository) -> str:
    """Create a test organization.

    Returns:
        Organization ID
    """
    org_data = OrganizationData(name="Test Organization", description="A test organization")
    org = test_repo.organizations.create(OrganizationCreateCommand(organization_data=org_data))
    return org.id


@pytest.fixture
def second_organization(test_repo: Repository) -> str:
    """Create a second test organization for cross-org testing.

    Returns:
        Organization ID
    """
    org_data = OrganizationData(name="Second Organization", description="Another test organization")
    org = test_repo.organizations.create(OrganizationCreateCommand(organization_data=org_data))
    return org.id
