"""Domain business data models for the project management application.

This module contains Pydantic models for representing the domain, API data validation and serialization.

The StubEntity models serve as a template/scaffolding for creating real domain entities.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StubEntityData(BaseModel):
    """Base data structure for stub entity - template for creating real entities."""

    name: str = Field(..., min_length=1, max_length=255, description="Stub entity name")
    description: Optional[str] = Field(None, max_length=1000, description="Stub entity description")


class StubEntity(StubEntityData):
    """Complete stub entity with metadata - template for creating real entities."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Stub entity ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class StubEntityCreateCommand(BaseModel):
    """Command model for creating a new stub entity - template for real create commands."""

    stub_entity_data: StubEntityData


class StubEntityUpdateCommand(BaseModel):
    """Command model for updating an existing stub entity - template for real update commands."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Stub entity name")
    description: Optional[str] = Field(None, max_length=1000, description="Stub entity description")
