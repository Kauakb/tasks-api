# the product rules. This layer knows nothing about HTTP: it raises domain
# errors, and errors.py turns them into HTTP responses
from psycopg import Connection

import repository


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def get_problem(conn: Connection, problem_id: int) -> dict:
    problem = repository.get_problem(conn, problem_id)
    if problem is None:
        raise NotFoundError(f"Problem {problem_id} not found")
    return problem


# the same title can't exist twice on one platform (except the problem itself)
def check_duplicate(
    conn: Connection, title: str, platform: str, problem_id: int | None = None
) -> None:
    existing = repository.find_problem_by_title(conn, title, platform)
    if existing is not None and existing["id"] != problem_id:
        raise ConflictError(f"Problem '{title}' already exists on {platform}")


def create_problem(conn: Connection, problem: dict) -> dict:
    check_duplicate(conn, problem["title"], problem["platform"])
    return repository.create_problem(conn, problem)


def list_problems(
    conn: Connection,
    topic: str | None,
    difficulty: str | None,
    platform: str | None,
) -> list[dict]:
    # topics are saved trimmed and lowercase, so the filter is too
    if topic is not None:
        topic = topic.strip().lower()
    return repository.list_problems(conn, topic, difficulty, platform)


def update_problem(conn: Connection, problem_id: int, changes: dict) -> dict:
    current = get_problem(conn, problem_id)
    # the title/platform pair after the change must still be unique
    title = changes.get("title", current["title"])
    platform = changes.get("platform", current["platform"])
    check_duplicate(conn, title, platform, problem_id)
    return repository.update_problem(conn, problem_id, changes)


def delete_problem(conn: Connection, problem_id: int) -> None:
    if not repository.delete_problem(conn, problem_id):
        raise NotFoundError(f"Problem {problem_id} not found")


def create_attempt(conn: Connection, problem_id: int, attempt: dict) -> dict:
    get_problem(conn, problem_id)  # 404 if the problem doesn't exist
    return repository.create_attempt(conn, problem_id, attempt)


def list_attempts(conn: Connection, problem_id: int) -> list[dict]:
    get_problem(conn, problem_id)  # 404 instead of an empty list
    return repository.list_attempts(conn, problem_id)
