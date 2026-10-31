# Interview Preparation Tracker

![CI](https://github.com/Kauakb/tasks-api/actions/workflows/ci.yml/badge.svg)

A local REST API that records the coding interview problems you practice
(LeetCode, HackerRank, CodeSignal) and every attempt at them: how long it
took, whether you solved it and how confident you felt. From that history,
it returns a **review queue**: the problems that most need practice, most
urgent first.

- **Single user**, no login.
- **No screen**: the API is the product. All calls are made with
  [Bruno](https://www.usebruno.com/), sending and receiving JSON.
- Runs **locally only**, on `http://127.0.0.1:8000`.

## Requirements

- Python 3.12 or newer
- PostgreSQL (tested with 18)
- Bruno (to use the request collection)

## Install and run

The commands below are for Windows PowerShell. On macOS/Linux, use
`.venv/bin/` instead of `.\.venv\Scripts\`.

```powershell
git clone https://github.com/Kauakb/tasks-api.git
cd tasks-api
python -m venv .venv
.\.venv\Scripts\pip install -r requirements-dev.txt
```

### Set up the database

1. Create two databases in PostgreSQL: one for the app and one for the tests.

   ```sql
   CREATE DATABASE tasks_api;
   CREATE DATABASE tasks_api_test;
   ```

2. Copy `.env.example` to `.env` and replace `CHANGE_ME` with your PostgreSQL
   password. `.env` is ignored by Git, so the password never gets committed.

   ```
   DATABASE_URL=postgresql://postgres:CHANGE_ME@localhost:5432/tasks_api
   TEST_DATABASE_URL=postgresql://postgres:CHANGE_ME@localhost:5432/tasks_api_test
   ```

The tables are created automatically the first time the API starts
(`tasks-api/schema.sql`). Without `DATABASE_URL`, the API refuses to start and
says which variable is missing.

### Start the API

```powershell
.\.venv\Scripts\python -m uvicorn main:app --app-dir tasks-api --reload
```

- Check it's up: `GET http://127.0.0.1:8000/health` returns `{"status": "ok"}`.
- Interactive docs (Swagger): http://127.0.0.1:8000/docs

## Run the tests

The tests use the `TEST_DATABASE_URL` database and empty it before each test,
so your real data is never touched.

```powershell
.\.venv\Scripts\pytest
.\.venv\Scripts\ruff check .
.\.venv\Scripts\ruff format --check .
```

## Use the Bruno collection

1. In Bruno, choose **Open Collection** and select the `bruno/` folder.
2. Select the **local** environment (it sets `base_url = http://127.0.0.1:8000`).
3. With the API running, open the collection's **Runner** and run everything.

The folders run in order: `Health`, `Problems`, `Attempts`, `Insights`, `Errors`.
"Create problem" saves the new problem's id in `{{problem_id}}`, and the next
requests use it. Every request has tests for the status and the body.

## Endpoints

| Method | Route | What it does | Success | Errors |
|---|---|---|---|---|
| GET | `/health` | Checks the API is up | 200 | - |
| POST | `/problems` | Creates a problem | 201 | 409, 422 |
| GET | `/problems` | Lists problems; optional filters `topic`, `difficulty`, `platform` | 200 | 422 |
| GET | `/problems/{id}` | Gets one problem | 200 | 404, 422 |
| PATCH | `/problems/{id}` | Changes only the fields sent | 200 | 404, 409, 422 |
| DELETE | `/problems/{id}` | Deletes a problem and its attempts | 204 | 404, 422 |
| POST | `/problems/{id}/attempts` | Logs an attempt | 201 | 404, 422 |
| GET | `/problems/{id}/attempts` | Attempt history, newest first | 200 | 404, 422 |
| GET | `/review?limit=5` | Review queue, most urgent first | 200 | 422 |

### Rules

- **Problem:** `title` (1-120 characters, trimmed), `platform` (`leetcode`,
  `codesignal`, `hackerrank` or `other`), `topic` (1-40 characters, saved in
  lowercase), `difficulty` (`easy`, `medium` or `hard`). The same title can't
  exist twice on the same platform (409).
- **Attempt:** `minutes` (1-600), `confidence` (1-5), `solved` (`true`/`false`),
  `notes` (optional, up to 500 characters). `created_at` is set by the API to
  today's date.

### Example

```http
POST /problems
{"title": "Valid Parentheses", "platform": "leetcode", "topic": "stack", "difficulty": "easy"}
```

```http
201 Created
{"id": 1, "title": "Valid Parentheses", "platform": "leetcode", "topic": "stack", "difficulty": "easy"}
```

### Review queue

`GET /review` scores each problem from its **most recent attempt**:

| Rule | Points |
|---|---|
| Not solved | +50 |
| Each confidence point below 5 | +10 |
| Each day since the attempt (at most 30) | +1 |

Example: not solved (+50), confidence 2 (3 points below 5, so +30), 4 days
ago (+4) = **84**.

- Highest score first. On a tie, the smaller `id` comes first.
- Problems with no attempts are left out.
- `limit` is optional: 5 by default, 1 to 50 (anything else is a 422).

```http
GET /review?limit=2
```

```json
[
  {"problem": {"id": 2, "title": "Valid Parentheses", "platform": "leetcode", "topic": "stack", "difficulty": "easy"}, "score": 84},
  {"problem": {"id": 1, "title": "Two Sum", "platform": "leetcode", "topic": "hashmap", "difficulty": "easy"}, "score": 31}
]
```

**How the queue is built.** SQL picks each problem's newest attempt
(`DISTINCT ON`, in `repository.latest_attempts`). A pure function
(`review.urgency`) gives each one a score. Then `sorted` orders them by
(-score, id) and the first `limit` items are returned.

- **Why `sorted` and not `heapq`:** `sorted` is **O(n log n)** for n
  problems. `heapq.nsmallest(limit, ...)` would be **O(n log k)** (k =
  limit), which only matters with a very large n. One person's catalog has
  hundreds of problems at most, so the simpler and more readable `sorted`
  wins.
- **Memory:** O(n), one score per problem.

### Errors

Every error has the same shape. Validation errors also list each invalid field.

```json
{"error": "NOT_FOUND", "message": "Problem 99 not found"}
```

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "fields": [{"field": "confidence", "message": "Input should be less than or equal to 5"}]
}
```

| `error` | Status |
|---|---|
| `NOT_FOUND` | 404 |
| `METHOD_NOT_ALLOWED` | 405 |
| `CONFLICT` | 409 |
| `VALIDATION_ERROR` | 422 |
| `INTERNAL_ERROR` | 500 (details go to the log, never to the response) |

## Technical decisions

- **PostgreSQL** instead of SQLite: it's what real backends use. Its
  constraints (`CHECK`, `UNIQUE`, foreign keys with `ON DELETE CASCADE`) protect
  the data even if a bug skips the API's validation.
- **SQL written by hand, no ORM.** Queries live in `tasks-api/repository.py`
  and always pass values as parameters (`%(name)s`), never by joining text, so
  input can't change a query (no SQL injection).
- **FastAPI + Pydantic:** request validation and the Swagger docs come built in.

### Layers

```
route (main.py) -> service (services.py) -> repository (repository.py) -> PostgreSQL
```

| Layer | File | Job |
|---|---|---|
| Route | `main.py` | Turns HTTP into Python calls and returns the right status. No product rules. |
| Service | `services.py` | Product rules (problem exists? duplicate?). Raises `NotFoundError` / `ConflictError` and knows nothing about HTTP. |
| Review | `review.py` | The urgency formula and the queue order, as pure functions (no database, no HTTP). |
| Repository | `repository.py` | The only place with SQL. |
| Errors | `errors.py` | Turns every error into the standard JSON shape. |
| Schemas | `schemas.py` | What JSON is accepted and returned (Pydantic). |

## Project structure

```
tasks-api/          the application
  main.py           routes
  services.py       product rules and domain errors
  review.py         review queue formula (pure functions)
  repository.py     SQL
  schema.sql        the two tables
  database.py       connection (psycopg)
  schemas.py        request/response shapes
  errors.py         standard error responses
  config.py         reads DATABASE_URL
tests/              pytest (uses the test database)
bruno/              Bruno collection
.github/workflows/  CI: ruff, pytest and pip-audit on every pull request
```
