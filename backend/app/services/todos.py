"""Business logic and SQL for ToDo items.

All database access for ToDo items happens here; routers only translate
HTTP requests into calls on these functions.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

_COLUMNS = "id, title, description, completed, created_at"


def _now() -> str:
    """Current UTC time as an ISO 8601 string, second precision."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _to_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["completed"] = bool(item["completed"])
    return item


def list_todos(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return every ToDo item, oldest first."""
    rows = connection.execute(
        f"SELECT {_COLUMNS} FROM todos ORDER BY id ASC"
    ).fetchall()
    return [_to_dict(row) for row in rows]


def get_todo(connection: sqlite3.Connection, todo_id: int) -> dict[str, Any] | None:
    """Return one ToDo item, or None when it does not exist."""
    row = connection.execute(
        f"SELECT {_COLUMNS} FROM todos WHERE id = ?", (todo_id,)
    ).fetchone()
    return None if row is None else _to_dict(row)


def create_todo(
    connection: sqlite3.Connection,
    title: str,
    description: str = "",
) -> dict[str, Any]:
    """Insert a new, uncompleted item and return it."""
    created_at = _now()
    with connection:
        cursor = connection.execute(
            """
            INSERT INTO todos (title, description, completed, created_at)
            VALUES (?, ?, 0, ?)
            """,
            (title.strip(), (description or "").strip(), created_at),
        )
    item = get_todo(connection, int(cursor.lastrowid))
    assert item is not None  # just inserted
    return item


def update_todo(
    connection: sqlite3.Connection,
    todo_id: int,
    *,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
) -> dict[str, Any] | None:
    """Apply the given changes to an item. Returns None when it is missing.

    The creation date is never modified.
    """
    if get_todo(connection, todo_id) is None:
        return None

    changes: dict[str, Any] = {}
    if title is not None:
        changes["title"] = title.strip()
    if description is not None:
        changes["description"] = description.strip()
    if completed is not None:
        changes["completed"] = 1 if completed else 0

    if changes:
        assignments = ", ".join(f"{column} = ?" for column in changes)
        with connection:
            connection.execute(
                f"UPDATE todos SET {assignments} WHERE id = ?",
                (*changes.values(), todo_id),
            )

    return get_todo(connection, todo_id)


def delete_todo(connection: sqlite3.Connection, todo_id: int) -> bool:
    """Delete an item permanently. Returns False when it did not exist."""
    with connection:
        cursor = connection.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    return cursor.rowcount > 0
