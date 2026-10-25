# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Early stage. The app lives in `tasks-api/main.py` (note the nested `tasks-api/` directory inside the repo root): a FastAPI app with two placeholder routes, `GET /` and `GET /about`. No database, tests, or linter yet.

## Setup

Dependencies are pinned in `requirements.txt` and installed into the project's `.venv`:

```
.venv\Scripts\pip install -r requirements.txt
```

## Running

```
.venv\Scripts\python -m uvicorn main:app --app-dir tasks-api --reload
```

Serves on http://127.0.0.1:8000 (interactive docs at `/docs`). `--reload` restarts the server when code changes.

## Bruno

The Bruno collection is in `bruno/` (one `.bru` file per request). Select the `local` environment, which sets `baseUrl`. Keep it in sync when endpoints change.

## Keeping this file current

When a database, tests, or lint tooling is added, update this file with the real commands (including how to run a single test) and a short architecture overview.
