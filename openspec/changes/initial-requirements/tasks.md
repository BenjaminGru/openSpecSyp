# Tasks

## 1. Project skeleton and dependencies

- [x] 1.1 Create `backend/app/` package (with `__init__.py`, `routers/`, `services/`), `backend/tests/`, and `frontend/css/`, `frontend/js/` directories, plus `.gitignore` entries for `__pycache__/`, `*.db`, and `.venv/`; verify the tree matches design.md section 1 and `git status` shows no ignored artifacts.
- [x] 1.2 Create `backend/requirements.txt` with `fastapi`, `uvicorn[standard]`, `pytest`, and `httpx`; verify installation in a virtualenv succeeds.
- [x] 1.3 Add a root `README.md` describing the stack, how to install dependencies, how to start the app with `uvicorn app.main:app --reload` from `backend/`, and the URLs for the public pages and `/api/todos`; verify every command in the README runs as written.

## 2. Database layer

- [x] 2.1 Implement `backend/app/database.py` with `connect()` (using `sqlite3`, `row_factory = sqlite3.Row`, path from `TODO_DB_PATH` defaulting to `backend/todos.db`) and `init_db()` running `CREATE TABLE IF NOT EXISTS todos` per design.md section 5; verify a fresh run creates the file with the expected columns via `PRAGMA table_info(todos)`.
- [x] 2.2 Verify `init_db()` is idempotent by calling it twice against the same file and confirming no error and unchanged schema.

## 3. Todo service and business logic

- [x] 3.1 Implement `backend/app/services/todos.py` with `list_todos`, `get_todo`, `create_todo`, `update_todo`, `delete_todo`, trimming titles, storing empty descriptions as `''`, setting `created_at` only on insert, and never changing `created_at` on update; verify with focused tests covering create defaults, update preserving id/created_at, and `None` for missing ids.
- [x] 3.2 Verify `list_todos` returns items in ascending `id` order and that `delete_todo` removes the row permanently.

## 4. REST API

- [x] 4.1 Define Pydantic models in `backend/app/schemas.py` (`TodoCreate`, `TodoUpdate`, `TodoRead`) with trimmed, non-blank titles up to 200 characters, descriptions up to 2000 characters, and `completed` as a boolean; verify valid/invalid payloads through API tests.
- [x] 4.2 Implement `GET /api/todos`, `POST /api/todos` (201), `GET /api/todos/{id}`, `PATCH /api/todos/{id}`, and `DELETE /api/todos/{id}` (204) in `backend/app/routers/todos.py`, using the `get_db` dependency and returning 404 JSON for unknown ids; verify each status code and response body with API tests.
- [x] 4.3 Wire the router and `init_db()` lifespan into `backend/app/main.py` and verify `GET /api/todos` on an empty database returns `200 []`.
- [x] 4.4 Add `backend/tests/conftest.py` pointing `TODO_DB_PATH` at a temporary database and resetting the table between tests; verify the fixture isolates tests by creating an item in one test and asserting the list is empty in the next.
- [x] 4.5 Add `backend/tests/test_todos_api.py` covering full CRUD, empty list, blank title rejection, over-length title rejection, 404s for unknown ids on GET/PATCH/DELETE, completion toggle preserving title/description/created_at, and persistence across two app instances sharing one database file; verify `pytest` passes.

## 5. Public website

- [x] 5.1 Create `frontend/index.html` with the student introduction and links to About, Portfolio, and Contact sections; verify it loads at `/` with JavaScript disabled.
- [x] 5.2 Create `frontend/about.html` with biography, education, skills list, and interests sections populated with clearly marked placeholder content; verify every section is present and non-empty.
- [x] 5.3 Create `frontend/portfolio.html` with a `<article>` block per placeholder project showing title, description, technologies, and an optional link, plus an empty-state message that is hidden when projects exist; verify at least two sample projects render and a project with no link renders no empty anchor.
- [x] 5.4 Create `frontend/contact.html` with an email address as a `mailto:` link and no form element; verify the page has zero `<form>` elements.
- [x] 5.5 Create `frontend/css/styles.css` with shared layout, navigation, active-link styling, project cards, and ToDo list styles; verify all four public pages render consistently and are readable at desktop and mobile widths.
- [x] 5.6 Create `frontend/js/nav.js` that marks the current page's navigation link active; verify each of the four pages highlights only its own link.
- [x] 5.7 Mount the frontend with `StaticFiles(..., html=True)` at `/` after the API router in `backend/app/main.py` and add `backend/tests/test_pages.py` asserting each public page returns 200 with its key heading, `/` serves the homepage, and an unknown path returns 404; verify `pytest` passes.

## 6. ToDo List frontend

- [x] 6.1 Create `frontend/todos.html` with a create form, an error banner, an empty-state element, and a list container, linked to `css/styles.css` and `js/todos.js`; verify the page returns 200 and contains the form and list elements.
- [x] 6.2 Implement `frontend/js/todos.js` list rendering via `GET /api/todos`, displaying title, description, completion status, and a locally formatted creation date, using `textContent` rather than `innerHTML`; verify an existing item appears with all fields and that a title containing `<b>x</b>` renders as literal text.
- [x] 6.3 Implement create, edit, and cancel flows in `frontend/js/todos.js` using `POST` and `PATCH`, re-fetching the list after each mutation and keeping user input on validation errors; verify against a running backend that a new item appears and that a blank-title submit shows the error without creating a row.
- [x] 6.4 Implement completion toggling via `PATCH {completed}` and deletion with a `window.confirm` prompt followed by `DELETE`; verify a completed item is visually distinguishable, toggling back restores it, and cancelling the confirm leaves the row in place.
- [x] 6.5 Handle API and network failures with a visible error message that clears on the next successful request; verify by stopping the backend and triggering a load, then restarting it and retrying.

## 7. Documentation and integration check

- [x] 7.1 Document the API endpoints, request/response shapes, field limits, and error responses in `README.md`, and note the known limitation that the ToDo list has no access control; verify every documented endpoint exists by exercising it with `curl` or the interactive docs at `/docs`.
- [x] 7.2 Add a short "Customise your site" section to `README.md` naming the files that hold biography, projects, and contact details; verify the referenced files exist and contain the placeholder markers.
- [x] 7.3 Run the full test suite (`pytest` from `backend/`) and manually walk the acceptance path with a running app: all four public pages, then create → edit → complete → delete a ToDo item, restart the server, and confirm the remaining items are still listed.

## Workflow follow-up

- Archive the change with the archive workflow once implementation is reviewed and `openspec validate initial-requirements --strict` passes.
