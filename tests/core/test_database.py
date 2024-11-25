import os
from pathlib import Path
from unittest.mock import MagicMock

from sqlmodel import SQLModel

from app.db.init_db import create_all


async def test_create_all(tmpdir: str, monkeypatch: MagicMock) -> None:
    """
    Test that the function creates the required tables.

    Args:
        tmpdir (str): temporary directory.
        monkeypatch (MagicMock): monkeypatch object.
    """

    # Set up test database file in a temporary directory
    db_file = Path(tmpdir.join("test_db.sqlite"))

    # Patch the database file path
    monkeypatch.setattr("app.paths.DATABASE_FILE", db_file)

    # Ensure the test database does not exist before running the function
    if os.path.exists(db_file):
        os.remove(db_file)

    # Run the function
    await create_all(sqlmodel_create_all=True)

    # Check that the required tables have been created
    tables = SQLModel.metadata.tables
    assert "images" in tables
    assert "user" in tables
    assert "fake_table" not in tables
