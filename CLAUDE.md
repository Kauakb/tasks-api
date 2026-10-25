# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Early stage. The app lives in `tasks-api/main.py` (note the nested `tasks-api/` directory inside the repo root): a FastAPI app with two placeholder routes, `GET /` and `GET /about`. Tests are in `tests/`. No database yet.

## Setup

Dependencies are pinned in `requirements.txt` and installed into the project's `.venv`:

```
.\.venv\Scripts\pip install -r requirements.txt
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

## CI

`.github/workflows/ci.yml` runs the same three checks on every PR and on every push to `production`. The PR `production → main` stays open so each push gets checked.

## Bruno

The Bruno collection is in `bruno/` (one `.bru` file per request). Select the `local` environment, which sets `baseUrl`. Keep it in sync when endpoints change.

## Keeping this file current

When a database or new tooling is added, update this file with the real commands (including how to run a single test) and a short architecture overview.
