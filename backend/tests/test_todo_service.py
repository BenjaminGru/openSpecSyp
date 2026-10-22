"""Tests for the ToDo service: defaults, updates, ordering, deletion."""

from __future__ import annotations

import pytest

from app import database
from app.services import todos


@pytest.fixture
def connection(database_file):
    database.init_db()
    conn = database.connect()
    try:
        with conn:
            conn.execute("DELETE FROM todos")
        yield conn
    finally:
        conn.close()


def test_create_uses_defaults_and_trims_title(connection):
    item = todos.create_todo(connection, title="  Write tests  ")

    assert item["title"] == "Write tests"
    assert item["description"] == ""
    assert item["completed"] is False
    assert item["created_at"].endswith("+00:00")


def test_create_with_description(connection):
    item = todos.create_todo(connection, "Read spec", "  Cover every scenario  ")

    assert item["description"] == "Cover every scenario"


def test_update_preserves_id_and_created_at(connection):
    created = todos.create_todo(connection, "Old title", "Old description")

    updated = todos.update_todo(
        connection,
        created["id"],
        title="  New title ",
        description="New description",
        completed=True,
    )

    assert updated is not None
    assert updated["id"] == created["id"]
    assert updated["created_at"] == created["created_at"]
    assert updated["title"] == "New title"
    assert updated["description"] == "New description"
    assert updated["completed"] is True


def test_update_without_changes_returns_item(connection):
    created = todos.create_todo(connection, "Unchanged")

    result = todos.update_todo(connection, created["id"])

    assert result == created


def test_update_missing_item_returns_none(connection):
    assert todos.update_todo(connection, 9999, title="Nope") is None


def test_list_orders_by_id(connection):
    first = todos.create_todo(connection, "First")
    second = todos.create_todo(connection, "Second")
    third = todos.create_todo(connection, "Third")

    ids = [item["id"] for item in todos.list_todos(connection)]

    assert ids == [first["id"], second["id"], third["id"]]


def test_delete_removes_item_permanently(connection):
    item = todos.create_todo(connection, "Delete me")

    assert todos.delete_todo(connection, item["id"]) is True
    assert todos.get_todo(connection, item["id"]) is None
    assert todos.delete_todo(connection, item["id"]) is False
