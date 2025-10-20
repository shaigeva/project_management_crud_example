"""SQLAlchemy ORM data models for the project management application.

This module contains all SQLAlchemy ORM models for database operations.
This is part of the Data Access Layer (DAL) and should only contain
database-specific models and logic.

The StubEntityORM model serves as a template/scaffolding for creating real ORM models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base

# SQLAlchemy Base for all ORM models
Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string for use as primary key."""
    return str(uuid.uuid4())


# SQLAlchemy ORM Models
class StubEntityORM(Base):
    """SQLAlchemy ORM model for stub entities - template for creating real ORM models."""

    __tablename__ = "stub_entities"

    # Using String for UUID storage in SQLite (36 characters for standard UUID format)
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # Timestamps for audit tracking
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<StubEntity(id='{self.id}', name='{self.name}')>"
