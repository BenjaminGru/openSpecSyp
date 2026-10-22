"""REST endpoints for the private ToDo list."""

from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..database import get_db
from ..schemas import TodoCreate, TodoRead, TodoUpdate
from ..services import todos as todo_service

router = APIRouter(prefix="/api/todos", tags=["todos"])

NOT_FOUND = "Todo not found"


def _or_404(item: dict[str, Any] | None) -> dict[str, Any]:
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return item


@router.get("", response_model=list[TodoRead])
def list_todos(connection: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
    """Return all ToDo items."""
    return todo_service.list_todos(connection)


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TodoCreate,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    """Create a new ToDo item."""
    return todo_service.create_todo(
        connection,
        title=payload.title,
        description=payload.description,
    )


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(
    todo_id: int,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    """Return a single ToDo item."""
    return _or_404(todo_service.get_todo(connection, todo_id))


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    """Edit a ToDo item or change its completion status."""
    changes = payload.model_dump(exclude_unset=True)
    updated = todo_service.update_todo(connection, todo_id, **changes)
    return _or_404(updated)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    """Delete a ToDo item."""
    if not todo_service.delete_todo(connection, todo_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
