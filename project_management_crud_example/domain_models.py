"""Domain business data models for the project management application.

This module contains Pydantic models for representing the domain, API data validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemData(BaseModel):
    """Base data structure containing common item fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, max_length=1000, description="Item description")


class Item(ItemData):
    """Complete item entity with metadata such as item_id, timestamps, etc."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Item ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ItemCreateCommand(BaseModel):
    """Command model for creating a new item."""

    item_data: ItemData


class ItemUpdateCommand(BaseModel):
    """Command model for updating an existing item."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, max_length=1000, description="Item description")
