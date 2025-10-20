"""Shared dependency injection functions for FastAPI.

This module provides shared dependency functions that can be used across
the application and routers without creating circular imports.
"""

from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from project_management_crud_example.dal.sqlite.database import Database
from project_management_crud_example.dal.sqlite.repository import ItemRepository

# Global database instance
_db_instance: Database | None = None


def get_database(db_path: str = "items.db") -> Database:
    """Get or create the database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance


def get_db_session() -> Iterator[Session]:
    """Dependency to get database session."""
    db = get_database()
    with db.get_session() as session:
        yield session


def get_item_repo(session: Session = Depends(get_db_session)) -> ItemRepository:  # noqa: B008
    """Dependency to get item repository."""
    return ItemRepository(session)
