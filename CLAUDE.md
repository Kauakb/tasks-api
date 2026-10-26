# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Early stage. The app code lives in the nested `tasks-api/` directory inside the repo root. Tests are in `tests/`.

- `main.py`: the FastAPI app, with two placeholder routes, `GET /` and `GET /about`.
- `config.py`: a `Settings` class (pydantic-settings) that reads the database settings from `.env`. Import the shared `settings` object from here.
- `database.py`: builds the SQLAlchemy `engine` (PostgreSQL through the psycopg driver) from `settings`, plus `SessionLocal`, which opens a new session per call.
- `models.py`: `Base` (the parent of all models) and the `Problem` model (`problems` table). Allowed values and text rules belong in schemas, not here.
- `create_tables.py`: a script run by hand that creates the missing tables with `Base.metadata.create_all`. It never changes an existing table: after changing a model, drop the table and run it again. Switch to Alembic migrations before storing real data.

No endpoints use the database yet.

## Setup

Dependencies are pinned in `requirements.txt` and installed into the project's `.venv`:

```
.\.venv\Scripts\pip install -r requirements.txt
```

### Database

The app needs PostgreSQL running locally (Windows service `postgresql-x64-18`) with a `tasks_api` database. Connection settings go in a `.env` file at the repo root: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Only `DB_PASSWORD` is required; the others have defaults in `config.py`. `.env` is gitignored, so never commit it.

To test the connection:

```
$env:PYTHONPATH = "tasks-api"
.\.venv\Scripts\python -c "from sqlalchemy import text; from database import engine; print(engine.connect().execute(text('select version()')).scalar())"
```

To create the tables:

```
$env:PYTHONPATH = "tasks-api"
.\.venv\Scripts\python tasks-api\create_tables.py
```

## Running

```
.\.venv\Scripts\python -m uvicorn main:app --app-dir tasks-api --reload
```

Serves on http://127.0.0.1:8000 (interactive docs at `/docs`). `--reload` restarts the server when code changes.

## Tests and lint

Dev tools (ruff, pytest, httpx) are in `requirements-dev.txt`:

```
.\.venv\Scripts\pip install -r requirements-dev.txt
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check .
.\.venv\Scripts\pytest
.\.venv\Scripts\pytest tests/test_main.py::test_home
```

The last line runs a single test. Config is in `pyproject.toml`: `tasks-api/` is on pytest's import path (the hyphen means it can't be a package), and ruff treats it as first-party code.

Run `ruff format --check .` on its own before pushing. With PowerShell's `;`, a ruff failure is easy to miss behind pytest's output.

## CI

`.github/workflows/ci.yml` runs the same three checks on every PR and on every push to `production`. The PR `production → main` stays open so each push gets checked. CI has no PostgreSQL and no `.env` yet. Both are needed once tests import `database.py`.

## Bruno

The Bruno collection is in `bruno/` (one `.bru` file per request). Select the `local` environment, which sets `baseUrl`. Keep it in sync when endpoints change.

## Keeping this file current

When a database or new tooling is added, update this file with the real commands (including how to run a single test) and a short architecture overview.
