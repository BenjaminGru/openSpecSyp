"""Schema tests for the SQLite database."""

from __future__ import annotations

from app import database

EXPECTED_COLUMNS = {"id", "title", "description", "completed", "created_at"}


def _table_info(connection) -> dict[str, dict]:
    rows = connection.execute("PRAGMA table_info(todos)").fetchall()
    return {row["name"]: dict(row) for row in rows}


def test_init_db_creates_expected_columns(database_file):
    database.init_db()

    connection = database.connect()
    try:
        columns = _table_info(connection)
    finally:
        connection.close()

    assert set(columns) == EXPECTED_COLUMNS
    assert columns["title"]["notnull"] == 1
    assert columns["description"]["notnull"] == 1
    assert columns["completed"]["notnull"] == 1
    assert columns["created_at"]["notnull"] == 1
    assert columns["id"]["pk"] == 1


def test_init_db_is_idempotent(database_file):
    database.init_db()

    connection = database.connect()
    try:
        before = _table_info(connection)
    finally:
        connection.close()

    database.init_db()

    connection = database.connect()
    try:
        after = _table_info(connection)
    finally:
        connection.close()

    assert before == after


def test_db_path_uses_environment_override(database_file):
    assert database.db_path() == database_file
