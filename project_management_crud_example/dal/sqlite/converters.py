"""Conversion functions between domain models and ORM models.

This module provides conversion functions to bridge between Pydantic domain models
and SQLAlchemy ORM models, maintaining clean separation of concerns while
enabling seamless data flow between layers.

All conversion functions are explicit and type-safe, avoiding the use of
model_validate() to ensure clear separation and evolution paths between
ORM and business models.
"""

from typing import List

from project_management_crud_example import domain_models
from project_management_crud_example.dal.sqlite import orm_data_models


def orm_item_to_business_item(orm_item: orm_data_models.ItemORM) -> domain_models.Item:
    """Convert an ORM Item model to a business Item model.

    This provides explicit type safety and clear conversion logic,
    avoiding the hidden coupling of model_validate().
    """
    return domain_models.Item(
        id=str(orm_item.id),
        name=orm_item.name,  # type: ignore[arg-type]
        description=orm_item.description,  # type: ignore[arg-type]
        created_at=orm_item.created_at,  # type: ignore[arg-type]
        updated_at=orm_item.updated_at,  # type: ignore[arg-type]
    )


def orm_items_to_business_items(orm_items: List[orm_data_models.ItemORM]) -> List[domain_models.Item]:
    """Convert a list of ORM Items to business Items."""
    return [orm_item_to_business_item(orm_item) for orm_item in orm_items]
