"""Shared fixtures: one temporary database file for the whole test session."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session")
def database_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Point the application at a throwaway database before it is imported."""
    path = tmp_path_factory.mktemp("data") / "test_todos.db"
    os.environ["TODO_DB_PATH"] = str(path)
    return path


@pytest.fixture(scope="session")
def fastapi_app(database_file: Path):
    """The FastAPI application bound to the temporary database."""
    from app.main import app

    return app


@pytest.fixture
def client(fastapi_app) -> Iterator["object"]:
    """A TestClient with an empty todos table for each test."""
    from fastapi.testclient import TestClient

    from app.database import connect

    with TestClient(fastapi_app) as test_client:
        connection = connect()
        try:
            with connection:
                connection.execute("DELETE FROM todos")
                connection.execute("DELETE FROM sqlite_sequence WHERE name = 'todos'")
        finally:
            connection.close()
        yield test_client
