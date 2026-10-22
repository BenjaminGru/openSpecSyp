"""FastAPI application: JSON API plus the static frontend."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routers import todos

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title="Student Portfolio and ToDo List",
    description="Public student website and a private, single-user ToDo list.",
    lifespan=lifespan,
)

app.include_router(todos.router)

# Mounted last so the API routes win. html=True serves index.html for "/"
# and 404.html for unknown paths.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
