# Student Portfolio and ToDo List

A small educational web application: a public website that introduces a student,
plus a private single-user ToDo list. The backend is Python/FastAPI, the frontend
is plain HTML, CSS, and JavaScript, and ToDo items are stored in SQLite.

## Stack

- Backend: Python 3.11+ with FastAPI and Uvicorn
- Frontend: HTML, CSS, JavaScript (no framework, no build step)
- Database: SQLite (accessed only by the backend)
- API: REST/JSON

## Project structure

```
backend/
  app/
    main.py            # FastAPI app, startup, static file mount
    database.py        # SQLite connections + schema
    schemas.py         # request/response models and validation
    services/todos.py  # business logic and SQL
    routers/todos.py   # /api/todos endpoints
  tests/               # pytest suite
  requirements.txt
frontend/
  index.html           # homepage
  about.html           # biography, education, skills, interests
  portfolio.html       # project list
  contact.html         # contact details
  todos.html           # private ToDo list
  404.html
  css/styles.css
  js/nav.js
  js/todos.js
```

## Setup

From the repository root:

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows (bash)
# source .venv/bin/activate   # macOS / Linux
python -m pip install -r backend/requirements.txt
```

## Run

```bash
cd backend
uvicorn app.main:app --reload
```

Then open:

| URL | Page |
| --- | --- |
| <http://127.0.0.1:8000/> | Homepage |
| <http://127.0.0.1:8000/about.html> | About |
| <http://127.0.0.1:8000/portfolio.html> | Portfolio |
| <http://127.0.0.1:8000/contact.html> | Contact |
| <http://127.0.0.1:8000/todos.html> | ToDo list (not linked from the public navigation) |
| <http://127.0.0.1:8000/docs> | Interactive API documentation |

The SQLite database file is created as `backend/todos.db` on first start. To use a
different location, set the `TODO_DB_PATH` environment variable to a file path.

## ToDo API

All endpoints accept and return JSON. A ToDo item looks like this:

```json
{
  "id": 1,
  "title": "Write documentation",
  "description": "Cover every endpoint",
  "completed": false,
  "created_at": "2026-10-21T09:47:00+00:00"
}
```

| Method | Path | Body | Success |
| --- | --- | --- | --- |
| `GET` | `/api/todos` | — | `200` with an array of items, oldest first |
| `POST` | `/api/todos` | `{"title": "...", "description": "..."}` | `201` with the created item |
| `GET` | `/api/todos/{id}` | — | `200` with the item |
| `PATCH` | `/api/todos/{id}` | any of `title`, `description`, `completed` | `200` with the updated item |
| `DELETE` | `/api/todos/{id}` | — | `204` with no body |

Field rules:

- `title` is required, is trimmed, must not be empty, and is limited to 200 characters.
- `description` is optional (defaults to an empty string) and limited to 2000 characters.
- `completed` is a boolean and defaults to `false` for new items.
- `created_at` is set by the backend in UTC, ISO 8601 format, and never changes.

Errors:

- `422` when validation fails, using FastAPI's standard `{"detail": [...]}` format.
- `404` with `{"detail": "Todo not found"}` when the id does not exist.

Example session:

```bash
curl -X POST http://127.0.0.1:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Write documentation","description":"Cover every endpoint"}'

curl http://127.0.0.1:8000/api/todos
curl -X PATCH http://127.0.0.1:8000/api/todos/1 \
  -H "Content-Type: application/json" -d '{"completed":true}'
curl -X DELETE http://127.0.0.1:8000/api/todos/1
```

## Tests

```bash
cd backend
../.venv/Scripts/python -m pytest      # Windows (bash)
# ../.venv/bin/python -m pytest        # macOS / Linux
```

The suite uses a temporary database, so running it never touches `backend/todos.db`.

## Customise your site

All public content is hand-written HTML — edit the files directly and reload:

| What to change | File | Look for |
| --- | --- | --- |
| Name in the header, introduction | `frontend/index.html` | `PLACEHOLDER` comment |
| Biography | `frontend/about.html` | `<!-- PLACEHOLDER: Replace the biography... -->` |
| Education entries | `frontend/about.html` | `<!-- PLACEHOLDER: Replace the education entries. -->` |
| Skills | `frontend/about.html` | `<!-- PLACEHOLDER: Replace the skills... -->` |
| Interests | `frontend/about.html` | `<!-- PLACEHOLDER: Replace the interests... -->` |
| Projects | `frontend/portfolio.html` | `PLACEHOLDER` comment above `.project-grid` |
| Email, links, location | `frontend/contact.html` | `PLACEHOLDER` comment |
| Colours and spacing | `frontend/css/styles.css` | `:root` variables |

Each portfolio project is an `<article class="project">` block. Copy one block per
project and delete the block when a project goes away; the empty-state note appears
automatically when no project blocks remain. Links are optional — leave out the
`<a class="project-link">` element.

The student name also appears in the page titles and footers of each HTML file.

## Known limitations

- The ToDo list has **no access control**: it is "private" only in the sense that it
  is not linked from the public navigation. Anyone who knows the URL can read and
  change the items. User accounts, authentication, and roles are out of scope for
  this version.
- Single user only; all items live in one shared list.
- No schema migrations: the table is created with `CREATE TABLE IF NOT EXISTS` at
  startup, so column changes require a manual database update.
