# Design

## Context

The repository currently contains only OpenSpec planning material; there is no application code yet. See `proposal.md` — Why for motivation. The constraints that shape this design come from the project context in `openspec/config.yaml` and from the delta specs:

- Frontend is plain HTML, CSS, and JavaScript in `frontend/` with no framework and no build step.
- Backend is Python + FastAPI in `backend/`, owns all business logic and all database access.
- SQLite is the only datastore; the browser never touches it.
- Single user, no auth, no roles — deliberately small and educational.

## Goals / Non-Goals

**Goals:**

- One FastAPI process serves both the static public site and the JSON API, so a single command runs the whole application.
- A Todo data model and REST contract that map one-to-one onto the requirements in `specs/todo-list/spec.md`.
- Obvious, readable layering: HTTP layer → service layer → SQLite, with tests that exercise the API end to end.
- Content that a student can edit by hand without touching Python or JavaScript.

**Non-Goals:**

- Authentication, sessions, per-user data, or any protection of the ToDo page (a recorded limitation, see Risks).
- ORM, migrations framework, or a database server — a single SQLite file is enough.
- Server-side templating for the public pages; they stay static files.
- A backend API for portfolio/about/homepage content.
- Deployment automation; running locally with Uvicorn is sufficient.

## Decisions

### 1. Directory layout

```
backend/
  app/
    __init__.py
    main.py            # FastAPI app, lifespan, static mount, routers
    database.py        # connection factory + schema initialisation
    schemas.py         # Pydantic request/response models
    services/todos.py  # business logic + SQL
    routers/todos.py   # /api/todos endpoints
  requirements.txt
  tests/
    conftest.py
    test_todos_api.py
    test_pages.py
frontend/
  index.html
  about.html
  portfolio.html
  contact.html
  todos.html
  css/styles.css
  js/todos.js
  js/nav.js
```

**Why:** keeps the "business logic in the backend, no DB access from the frontend" rule physically visible, and separates the HTTP layer from SQL so each is small enough to read in one sitting. `/backend` and `/frontend` match the paths fixed in the project context.

**Alternative considered:** a flat `main.py` plus one `index.html`. Rejected because the ToDo CRUD logic would leak into route handlers and the layering the project rules require would be invisible.

### 2. Static pages are hand-written HTML with duplicated navigation

Every page is a complete HTML document; the shared navigation markup is repeated in each file. `js/nav.js` only marks the current page's nav link as active by comparing `location.pathname` to each link's `href` (and a `data-page` attribute as a fallback). No template engine. Site CSS lives in one `styles.css`.

**Why:** no build step, no framework, and the pages stay readable with JavaScript disabled. Duplicating five nav blocks is cheaper to understand than adding Jinja or a JS renderer.

**Alternative considered:** server-side Jinja templates. Rejected — it adds a dependency and couples content to the backend for four static pages.

### 3. FastAPI serves the frontend with `StaticFiles`

`main.py` includes the API router first, then mounts `StaticFiles(directory=frontend, html=True)` at `/`. `html=True` maps `/` to `index.html`; navigation links use explicit `.html` suffixes (e.g. `/about.html`) so the mapping is unambiguous, and unknown paths fall through to the static app's 404.

**Why:** one origin, no CORS configuration, `fetch('/api/todos')` works with relative URLs.

**Alternative considered:** serving the frontend from a separate dev server. Rejected — it needs CORS and a second process, and the assignment wants one simple application.

**Alternative considered:** explicit `FileResponse` routes per page. Rejected as more code for no benefit; only the 404 page would need a custom handler, which is unnecessary for the initial version.

### 4. SQLite access through the standard library, one connection per request

`database.py` exposes `connect()` (configured with `row_factory = sqlite3.Row`) and `init_db()` which runs `CREATE TABLE IF NOT EXISTS todos (...)`. FastAPI dependency injection provides a connection to each request:

```python
def get_db():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
```

`init_db()` is called once from the app's `lifespan`. Endpoints are declared as plain `def` (not `async def`) so FastAPI runs them in the worker threadpool and the blocking `sqlite3` calls never stall the event loop. Because each request owns its connection, no cross-thread sharing of a connection occurs.

**Why:** dependency injection is a project rule; a per-request connection avoids `check_same_thread=False` hacks and is trivially safe.

**Alternative considered:** SQLAlchemy + ORM. Rejected for the initial version — extra dependency, extra config, and the schema is one table.

**Alternative considered:** one long-lived global connection. Rejected — unsafe across threadpool workers.

Database file: `backend/todos.db`, overridable with the `TODO_DB_PATH` environment variable (tests point it at a temp file). It is created on first start and gitignored.

### 5. Todo schema

```sql
CREATE TABLE IF NOT EXISTS todos (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  title       TEXT    NOT NULL,
  description TEXT    NOT NULL DEFAULT '',
  completed   INTEGER NOT NULL DEFAULT 0,   -- 0 / 1
  created_at  TEXT    NOT NULL              -- ISO 8601 UTC
);
```

- `title` is trimmed and required, max 200 characters.
- `description` is optional; missing input is stored as `''`, max 2000 characters.
- `completed` is stored as 0/1 and exposed as a JSON boolean.
- `created_at` is set by the backend on insert only, never on update, using `datetime.now(timezone.utc).isoformat(timespec="seconds")`.
- JSON representation (Pydantic model): `{ "id": 1, "title": "...", "description": "...", "completed": false, "created_at": "2026-10-21T09:47:00+00:00" }`.

**Why:** flat table, primitive types, no joins — appropriate for the teaching goal. Storing timestamps as ISO strings keeps the DB file human-inspectable.

**Alternative considered:** separate `created_at` as Unix epoch integer. Rejected — the API must return ISO 8601 anyway, and readable rows help during debugging.

### 6. REST contract

| Method | Path | Body | Success | Errors |
| --- | --- | --- | --- | --- |
| GET | `/api/todos` | — | 200, array (oldest first, by `id`) | — |
| POST | `/api/todos` | `{title, description?}` | 201, created item | 422 invalid input |
| GET | `/api/todos/{id}` | — | 200, item | 404 |
| PATCH | `/api/todos/{id}` | any of `{title, description, completed}` | 200, updated item | 404, 422 |
| DELETE | `/api/todos/{id}` | — | 204, no body | 404 |

- `PATCH` is used for both content edits and completion toggles; omitted fields are left untouched. This keeps the frontend to one update call for both actions.
- Validation is expressed in Pydantic models (`field_validator` trims and rejects blank titles), so 422 responses come from FastAPI's standard validation error format; missing IDs raise `HTTPException(404)` with `{"detail": "Todo not found"}`.
- Errors are always JSON. The frontend surfaces `detail` (or a generic message) in an inline error area.

**Why:** `PATCH` + partial bodies maps cleanly onto "edit" and "toggle complete" without inventing a second endpoint. Returning the full item on write lets the frontend re-render without a follow-up GET.

**Alternative considered:** `PUT /api/todos/{id}` with a complete body for edits and a dedicated `/complete` endpoint. Rejected as more surface area for the same behavior.

### 7. Layering and service API

`services/todos.py` exposes `list_todos(conn)`, `get_todo(conn, id)`, `create_todo(conn, title, description)`, `update_todo(conn, id, fields)`, `delete_todo(conn, id)`. The router converts rows to Pydantic models and maps `None` results to 404. No SQL outside the service and `database.py`.

**Why:** satisfies "business logic belongs in the backend" and keeps the router free of SQL; unit tests can call the service directly.

### 8. Frontend ToDo page (`todos.html` + `js/todos.js`)

- On load: `GET /api/todos`, render each item as a `<li>` with checkbox (completion), title, description, creation date (shown in the browser's local timezone via `toLocaleString`), Edit and Delete buttons.
- Create: a form above the list; `POST` on submit, then re-fetch the list.
- Edit: replaces the item's display with a form pre-filled with its values; Save sends `PATCH` with `{title, description}`, Cancel restores the display.
- Complete: checkbox sends `PATCH` with `{completed}`; the list is re-fetched so the ordering and styling stay consistent.
- Delete: `window.confirm` first, then `DELETE`, then re-fetch.
- A single `setError(message)` helper renders API and network failures in a visible error banner; form inputs keep their values on failure.
- All content is inserted with `textContent`/`createElement`, never `innerHTML`, so titles and descriptions cannot inject markup.

**Why:** re-fetching after each mutation is the simplest correct state model for a list this size and avoids hand-maintained client-side state.

**Alternative considered:** optimistic local updates. Rejected — more code paths to get wrong for no visible gain in a single-user list.

### 9. Testing approach

`pytest` with `fastapi.testclient.TestClient`. `conftest.py` sets `TODO_DB_PATH` to a temporary file (or in-memory connection factory) before creating the app and truncates the table between tests. Tests cover: full CRUD round trip, empty list, blank title rejection, over-length title, unknown ID 404s on GET/PATCH/DELETE, creation date unchanged on edit, completion toggle preserving other fields, and persistence across a second app instance using the same DB file. `test_pages.py` asserts each public page returns 200 with expected headings and that an unknown path returns 404.

**Why:** the specs are scenario-based, so one test per scenario is a direct check of the contract, including the persistence requirement that is otherwise easy to fake.

## Risks / Trade-offs

- **The ToDo list has no access control** → It is documented as a known limitation ("private" here means not advertised in the public navigation). Mitigation: keep the page unlinked from public nav, and note that adding auth is a separate future change.
- **No schema migrations** → Changing columns later needs a manual step. Mitigation: `CREATE TABLE IF NOT EXISTS` on startup now; keep the single-table schema stable for the initial version.
- **SQLite write locking under concurrency** → Single user, short transactions, per-request connections. Mitigation: acceptable for the course scope; revisit if concurrent writers appear.
- **Duplicated markup across five public pages** → Navigation edits must be applied five times. Mitigation: `nav.js` centralises the active-link logic and the nav block is small; a templating layer can come later if the site grows.
- **Portfolio content lives in HTML** → Publishing a project means editing markup. Mitigation: keep each project in a consistent `<article>` block with clear placeholder comments.
- **Blocking `sqlite3` in sync endpoints** → Uses the threadpool; fine at this scale. Mitigation: avoid `async def` handlers with direct DB calls.
- **Timestamps are UTC while the UI shows local time** → Potential confusion if a student compares DB rows to the page. Mitigation: format dates for display and keep the API in ISO 8601 UTC.
- **Placeholder personal content** → The site ships with sample biography, projects, and contact details. Mitigation: mark placeholders clearly in `tasks.md` so they are replaced before submission.

## Open Questions

- Final content (student name, real biography, project list, contact address) is supplied by the student; only placeholders are used during implementation.
