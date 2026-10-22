"""SQLite connection handling and schema initialisation."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "todos.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS todos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    completed   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL
);
"""


def db_path() -> Path:
    """Return the database file to use, honouring the TODO_DB_PATH override."""
    configured = os.getenv("TODO_DB_PATH")
    return Path(configured) if configured else DEFAULT_DB_PATH


def connect() -> sqlite3.Connection:
    """Open a new connection with row access by column name."""
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the schema if it does not exist yet. Safe to call repeatedly."""
    connection = connect()
    try:
        with connection:
            connection.execute(SCHEMA)
    finally:
        connection.close()


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency yielding one connection per request."""
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()
