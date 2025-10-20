"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from project_management_crud_example.app import app
from project_management_crud_example.dal.sqlite.database import Database
from project_management_crud_example.dal.sqlite.repository import ItemRepository
from project_management_crud_example.dependencies import get_db_session


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options."""
    parser.addoption(
        "--db-mode",
        action="store",
        default="disk",
        choices=["memory", "disk"],
        help="Database mode: 'memory' for in-memory SQLite, 'disk' for file-based (default: disk)",
    )


@pytest.fixture
def db_path(request: pytest.FixtureRequest) -> Generator[str, None, None]:
    """Provide database path based on --db-mode parameter.

    - In 'disk' mode (default): Creates a temporary file for each test
    - In 'memory' mode: Returns ':memory:' for in-memory database

    Each test gets its own isolated database.
    """
    db_mode = request.config.getoption("--db-mode")

    if db_mode == "memory":
        yield ":memory:"
    else:
        # Create a temporary directory and file for this test
        with tempfile.TemporaryDirectory() as temp_dir:
            db_file = Path(temp_dir) / f"test_{request.node.name}.db"
            yield str(db_file)
            # Cleanup happens automatically when temp_dir context exits


@pytest.fixture
def test_db(db_path: str) -> Generator[Database, None, None]:
    """Create a fresh database for each test.

    This fixture ensures each test gets a completely isolated database
    that is automatically cleaned up after the test completes.
    Uses disk-based SQLite by default (respects --db-mode parameter).
    """
    db = Database(db_path, is_testing=True)
    db.create_tables()
    yield db
    db.drop_tables()
    db.dispose()


@pytest.fixture
def test_session(test_db: Database) -> Generator[Session, None, None]:
    """Get a database session for testing.

    This fixture provides a database session that is automatically
    committed and closed after each test.
    """
    with test_db.get_session() as session:
        yield session


@pytest.fixture
def test_item_repo(test_session: Session) -> ItemRepository:
    """Get an item repository for testing.

    This fixture provides an ItemRepository instance connected to the
    test database session.
    """
    return ItemRepository(test_session)


@pytest.fixture
def client(test_db: Database) -> Generator[TestClient, None, None]:
    """Standardized FastAPI TestClient fixture for all API tests.

    - Ensures every test gets a fresh, isolated database (disk-based by default).
    - Overrides the get_db_session dependency to use the test database.
    - Cleans up dependency overrides after each test to prevent leakage.
    - All API tests MUST use this fixture for client access.
    """

    def override_get_db_session() -> Generator[Session, None, None]:
        with test_db.get_session() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as test_client:
        yield test_client

    # Reset dependency overrides to prevent test interference
    app.dependency_overrides = {}
