# Proposal

## Why

The project starts from an empty repository. A student needs a single application that presents them publicly (introduction, background, projects, contact details) and also provides a small private productivity tool. Building both parts in one FastAPI + SQLite application keeps the setup small enough for an educational software project while still demonstrating a clean frontend/backend split over a REST API.

## What Changes

- Add a public, static-content website with four pages: Homepage, About, Portfolio, and Contact.
- Add a private ToDo List page backed by a REST API.
- Add a FastAPI backend that serves the REST API and the static frontend files.
- Add a SQLite database for persisting ToDo items, accessed only by the backend.
- Add a project skeleton (`backend/`, `frontend/`) and local run instructions.
- No user registration, authentication, roles, or multi-user support in this version.

## Capabilities

### New Capabilities

- `public-website`: The public pages that introduce the student — homepage summary, about/biography/education/skills/interests, portfolio project list, and contact details — plus the site navigation that connects them.
- `todo-list`: The private ToDo list — viewing, creating, editing, completing, and deleting ToDo items through a REST API, with items persisted in SQLite across application restarts.

### Modified Capabilities

None — this is the first change in the project; no specs exist yet.

## Impact

- New directories `backend/` (FastAPI app, business logic, database access) and `frontend/` (HTML, CSS, JavaScript).
- New REST endpoints under `/api/todos` and static page routes serving the frontend.
- New SQLite database file created by the backend at startup.
- Python dependencies: FastAPI and an ASGI server (Uvicorn); SQLite access via the Python standard library.
- Content for the public pages (student name, biography, projects, contact details) is placeholder data to be replaced by the student.
