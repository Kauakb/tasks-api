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

The app needs PostgreSQL running locally (Windows service `postgresql-x64-18`) with a `tasks_api` database. Connection settings go in a `.env` file at the repo root: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Only `DB_PASSWORD` is required; the others have defaults in `config.py`. Start from `.env.example` (copy it to `.env`). `.env` and `.env.*` are gitignored, so never commit them; `.env.example` is the one exception and must stay free of real values.

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

Serves on http://127.0.0.1:8000 (interactive docs at `/docs`). `--reload` restarts the server when code changes. Keep the default `127.0.0.1` host: the API has no auth, so `--host 0.0.0.0` would expose it to the network.

## Tests and lint

Dev tools (ruff, pytest, httpx, pip-audit) are in `requirements-dev.txt`:

```
.\.venv\Scripts\pip install -r requirements-dev.txt
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check .
.\.venv\Scripts\pytest
.\.venv\Scripts\pytest tests/test_main.py::test_home
.\.venv\Scripts\pip-audit -r requirements-dev.txt
```

`pytest tests/test_main.py::test_home` runs a single test. `pip-audit` fails when a pinned package has a known vulnerability. Config is in `pyproject.toml`: `tasks-api/` is on pytest's import path (the hyphen means it can't be a package), and ruff treats it as first-party code.

Before every push, run all four checks with this command. It stops at the first failure, so a ruff error can't hide behind pytest's output:

```
.\.venv\Scripts\ruff check .; if ($?) { .\.venv\Scripts\ruff format --check . }; if ($?) { .\.venv\Scripts\pytest }; if ($?) { .\.venv\Scripts\pip-audit -r requirements-dev.txt }
```

`if ($?)` runs the next command only if the last one succeeded (PowerShell 5.1 has no `&&`).

## CI

`.github/workflows/ci.yml` runs the same four checks on every PR and on every push to `develop`, with a read-only token (`permissions: contents: read`). `main` is protected: the `checks` job must pass, and force-push and deletion are blocked. CI sets a placeholder `DB_PASSWORD` for the pytest step, because `main.py` imports `database.py` and `Settings()` requires it. There's no PostgreSQL service yet, so tests must not query the database. Add one (with a matching password) before writing tests that do.

## Security

The repo is public. GitHub secret scanning with push protection, Dependabot alerts and security updates, CodeQL (default setup) and private vulnerability reporting are on. `.github/dependabot.yml` opens weekly update PRs for pip and GitHub Actions against `develop`; Dependabot security-fix PRs target `main` (the default branch). `SECURITY.md` tells reporters to use the private report form.

## Bruno

The Bruno collection is in `bruno/` (one `.bru` file per request). Select the `local` environment, which sets `baseUrl`. Keep it in sync when endpoints change.

## Keeping this file current

When a database or new tooling is added, update this file with the real commands (including how to run a single test) and a short architecture overview.
