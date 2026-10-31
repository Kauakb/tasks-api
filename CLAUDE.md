# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

The spec is the PRD *Interview Preparation Tracker* v1.0 (15 user stories, GitHub issues #13-#27, US-n = #(12+n)). Built so far: US-01 to US-11, US-13 and US-14. Not built: US-12 (stats). The review formula (US-11) is fixed by the PRD; explain any change to it before making it.

The app code lives in the nested `tasks-api/` directory inside the repo root. Tests are in `tests/`. The PRD forbids an ORM: SQL is written by hand. Layers, in order:

- `main.py`: routes only. Turns HTTP into calls to `services` and returns the right status. Gets a connection with `Db = Annotated[Connection, Depends(get_db)]`.
- `services.py`: product rules (existence, duplicate title per platform). Raises `NotFoundError` / `ConflictError` and knows nothing about HTTP.
- `review.py`: the review queue's urgency formula and ordering, as pure functions (no database, no HTTP). Fed by `repository.latest_attempts`.
- `repository.py`: the only file with SQL. Values always go in as parameters (`%(name)s`). Column names in dynamic SQL use `psycopg.sql.Identifier`.
- `errors.py`: exception handlers. Every error is `{"error": "CODE", "message": "..."}`, plus `fields` on 422.
- `schemas.py`: Pydantic request/response models. Allowed values and text rules live here (and as constraints in `schema.sql`).
- `database.py`: `connect()` (psycopg, `autocommit=True`, rows as dicts), `create_tables()` and the `get_db` dependency.
- `schema.sql`: the two tables. It runs on every startup (`CREATE TABLE IF NOT EXISTS`) and never changes an existing table: after changing it, drop the table in the dev database and restart.
- `config.py`: reads `DATABASE_URL`. The app exits with a clear message if it's missing.

## Setup

Dependencies are pinned in `requirements.txt` (app) and `requirements-dev.txt` (adds the dev tools), installed into the project's `.venv`:

```
.\.venv\Scripts\pip install -r requirements-dev.txt
```

### Database

PostgreSQL runs locally (Windows service `postgresql-x64-18`) with two databases: `tasks_api` (dev) and `tasks_api_test` (tests only). `.env` at the repo root sets `DATABASE_URL` and `TEST_DATABASE_URL`. Start from `.env.example`. `.env` and `.env.*` are gitignored, so never commit them. `.env.example` is the one exception and must stay free of real values.

## Running

```
.\.venv\Scripts\python -m uvicorn main:app --app-dir tasks-api --reload
```

Serves on http://127.0.0.1:8000 (interactive docs at `/docs`). Keep the default `127.0.0.1` host: the API has no auth, so `--host 0.0.0.0` would expose it to the network.

## Tests and lint

```
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check .
.\.venv\Scripts\pytest
.\.venv\Scripts\pytest tests/test_problems.py::test_create_problem
.\.venv\Scripts\pip-audit -r requirements-dev.txt
```

`tests/conftest.py` points `DATABASE_URL` at `TEST_DATABASE_URL` before importing the app. The `db` fixture truncates both tables (ids restart at 1), and `client` is a `TestClient` that runs the startup code. Config is in `pyproject.toml`: `tasks-api/` is on pytest's import path (the hyphen means it can't be a package).

Before every push, run all four checks with this command. It stops at the first failure:

```
.\.venv\Scripts\ruff check .; if ($?) { .\.venv\Scripts\ruff format --check . }; if ($?) { .\.venv\Scripts\pytest }; if ($?) { .\.venv\Scripts\pip-audit -r requirements-dev.txt }
```

`if ($?)` runs the next command only if the last one succeeded (PowerShell 5.1 has no `&&`). In PowerShell 5.1, a commit message containing `"` gets mangled by `git commit -m`; use `git commit -F <file>` instead.

## CI

`.github/workflows/ci.yml` runs the four checks on every PR and on every push to `develop`, with a read-only token. A `postgres:18` service container provides the test database (`TEST_DATABASE_URL` is set on the pytest step). `main` is protected: the `checks` job must pass.

## Git flow

Work goes on a feature branch, then a PR into `develop`. When a release is ready, a PR `develop` → `main` (squash-merge) closes the issues with `Closes #N`. After that merge, run `git merge origin/main` on `develop`, or the next `develop` → `main` PR conflicts.

## Security

The repo is public. GitHub secret scanning with push protection, Dependabot alerts and security updates, CodeQL (default setup) and private vulnerability reporting are on. `.github/dependabot.yml` opens weekly update PRs against `develop`. `SECURITY.md` tells reporters to use the private report form.

## Bruno

The collection is in `bruno/`, laid out as the PRD asks: folders `Health`, `Problems`, `Attempts`, `Insights`, `Errors`, ordered by `seq` in each `folder.bru`. The `local` environment sets `base_url`. "Create problem" saves `problem_id` and `problem_title` for the later requests. Every request has `tests`. Keep it in sync when endpoints change.
