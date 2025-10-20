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
