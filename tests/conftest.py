"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


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
