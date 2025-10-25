"""Conversion functions between domain models and ORM models.

This module provides conversion functions to bridge between Pydantic domain models
and SQLAlchemy ORM models, maintaining clean separation of concerns while
enabling seamless data flow between layers.

All conversion functions are explicit and type-safe, avoiding the use of
model_validate() to ensure clear separation and evolution paths between
ORM and business models.

The stub entity converters serve as a template/scaffolding for creating real converters.
"""

from typing import List

from project_management_crud_example import domain_models
from project_management_crud_example.dal.sqlite import orm_data_models


def orm_stub_entity_to_business_stub_entity(
    orm_stub_entity: orm_data_models.StubEntityORM,
) -> domain_models.StubEntity:
    """Convert an ORM StubEntity model to a business StubEntity model.

    This provides explicit type safety and clear conversion logic,
    avoiding the hidden coupling of model_validate().

    Template for creating real entity converters.
    """
    return domain_models.StubEntity(
        id=str(orm_stub_entity.id),
        name=orm_stub_entity.name,  # type: ignore[arg-type]
        description=orm_stub_entity.description,  # type: ignore[arg-type]
        created_at=orm_stub_entity.created_at,  # type: ignore[arg-type]
        updated_at=orm_stub_entity.updated_at,  # type: ignore[arg-type]
    )


def orm_stub_entities_to_business_stub_entities(
    orm_stub_entities: List[orm_data_models.StubEntityORM],
) -> List[domain_models.StubEntity]:
    """Convert a list of ORM StubEntities to business StubEntities.

    Template for creating real entity list converters.
    """
    return [orm_stub_entity_to_business_stub_entity(orm_stub_entity) for orm_stub_entity in orm_stub_entities]


def orm_organization_to_domain_organization(
    orm_organization: orm_data_models.OrganizationORM,
) -> domain_models.Organization:
    """Convert an ORM Organization model to a domain Organization model."""
    return domain_models.Organization(
        id=str(orm_organization.id),
        name=orm_organization.name,  # type: ignore[arg-type]
        description=orm_organization.description,  # type: ignore[arg-type]
        is_active=orm_organization.is_active,  # type: ignore[arg-type]
        created_at=orm_organization.created_at,  # type: ignore[arg-type]
        updated_at=orm_organization.updated_at,  # type: ignore[arg-type]
    )


def orm_project_to_domain_project(
    orm_project: orm_data_models.ProjectORM,
) -> domain_models.Project:
    """Convert an ORM Project model to a domain Project model."""
    return domain_models.Project(
        id=str(orm_project.id),
        name=orm_project.name,  # type: ignore[arg-type]
        description=orm_project.description,  # type: ignore[arg-type]
        organization_id=str(orm_project.organization_id),
        created_at=orm_project.created_at,  # type: ignore[arg-type]
        updated_at=orm_project.updated_at,  # type: ignore[arg-type]
    )


def orm_ticket_to_domain_ticket(
    orm_ticket: orm_data_models.TicketORM,
) -> domain_models.Ticket:
    """Convert an ORM Ticket model to a domain Ticket model."""
    return domain_models.Ticket(
        id=str(orm_ticket.id),
        title=orm_ticket.title,  # type: ignore[arg-type]
        description=orm_ticket.description,  # type: ignore[arg-type]
        status=domain_models.TicketStatus(orm_ticket.status),  # type: ignore[arg-type]
        priority=domain_models.TicketPriority(orm_ticket.priority) if orm_ticket.priority else None,  # type: ignore[arg-type]
        assignee_id=str(orm_ticket.assignee_id) if orm_ticket.assignee_id else None,
        reporter_id=str(orm_ticket.reporter_id),
        project_id=str(orm_ticket.project_id),
        created_at=orm_ticket.created_at,  # type: ignore[arg-type]
        updated_at=orm_ticket.updated_at,  # type: ignore[arg-type]
    )


def orm_user_to_domain_user(
    orm_user: orm_data_models.UserORM,
) -> domain_models.User:
    """Convert an ORM User model to a domain User model.

    Note: password_hash is NOT included in the domain User model for security.
    Passwords should only be handled by authentication utilities.
    """
    return domain_models.User(
        id=str(orm_user.id),
        username=orm_user.username,  # type: ignore[arg-type]
        email=orm_user.email,  # type: ignore[arg-type]
        full_name=orm_user.full_name,  # type: ignore[arg-type]
        organization_id=orm_user.organization_id,  # type: ignore[arg-type]
        role=domain_models.UserRole(orm_user.role),  # type: ignore[arg-type]
        is_active=orm_user.is_active,  # type: ignore[arg-type]
        created_at=orm_user.created_at,  # type: ignore[arg-type]
        updated_at=orm_user.updated_at,  # type: ignore[arg-type]
    )


def orm_user_to_user_auth_data(
    orm_user: orm_data_models.UserORM,
) -> domain_models.UserAuthData:
    """Convert an ORM User model to UserAuthData for authentication.

    This converter includes password_hash for authentication purposes only.
    UserAuthData should NEVER be exposed outside the authentication layer.

    Note: This maintains proper layering by returning a domain model, not an ORM object.
    """
    return domain_models.UserAuthData(
        id=str(orm_user.id),
        username=orm_user.username,  # type: ignore[arg-type]
        password_hash=orm_user.password_hash,  # type: ignore[arg-type]
        organization_id=orm_user.organization_id,  # type: ignore[arg-type]
        role=domain_models.UserRole(orm_user.role),  # type: ignore[arg-type]
        is_active=orm_user.is_active,  # type: ignore[arg-type]
    )
