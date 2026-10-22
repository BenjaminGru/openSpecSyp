# Project Architecture
## Technology Stack
- Backend: Python fastapi
- Programming language: Python
- Frontend: HTML, JavaScript
- Database: SQLite
- API: REST/JSON
## Architecture Overview
The project follows a modular architecture, separating concerns into
distinct layers. The backend is built using FastAPI, which provides a highperformance web framework for building APIs with Python. The frontend is
developed using HTML and JavaScript, allowing for dynamic and interactive
user interfaces. The database layer utilizes SQLite for
HTML/JavaScript Frontend
|
| REST/JSON
v
Python FastAPI Backend
|
v
SQLite
## Rules
- Business logic belongs in the backend.
- The frontend must never access the database directly.
- Use dependency injection in the backend.
- Use async APIs where appropriate.
- OpenSpec specifications are the source of truth for requirements.
## Project Management
- Rquirements are managed in OpenSpec.
- Use GitHub Projects for task management. (hopefully handled with OpenSpec)