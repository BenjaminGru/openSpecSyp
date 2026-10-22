"""Request and response models for the ToDo API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000

TITLE_REQUIRED = "title must not be empty"


def _clean_title(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(TITLE_REQUIRED)
    return cleaned


class TodoCreate(BaseModel):
    """Payload for creating a ToDo item."""

    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    description: str = Field(default="", max_length=MAX_DESCRIPTION_LENGTH)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _clean_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return value.strip()


class TodoUpdate(BaseModel):
    """Payload for editing a ToDo item. Omitted fields stay unchanged."""

    title: str | None = Field(default=None, max_length=MAX_TITLE_LENGTH)
    description: str | None = Field(default=None, max_length=MAX_DESCRIPTION_LENGTH)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        return None if value is None else _clean_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return None if value is None else value.strip()


class TodoRead(BaseModel):
    """A ToDo item as returned by the API."""

    id: int
    title: str
    description: str
    completed: bool
    created_at: str
