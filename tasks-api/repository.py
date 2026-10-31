# the only file with SQL. Values always go in as parameters (%(name)s),
# never glued into the SQL text, so user input can't change the query
# (that's what prevents SQL injection)
from psycopg import Connection, sql

# fixed column lists (never user input), reused by the queries below
PROBLEM_COLUMNS = "id, title, platform, topic, difficulty"
ATTEMPT_COLUMNS = "id, problem_id, minutes, confidence, solved, notes, created_at"


def create_problem(conn: Connection, problem: dict) -> dict:
    return conn.execute(
        f"""
        INSERT INTO problems (title, platform, topic, difficulty)
        VALUES (%(title)s, %(platform)s, %(topic)s, %(difficulty)s)
        RETURNING {PROBLEM_COLUMNS}
        """,
        problem,
    ).fetchone()


# each filter is optional: when it's None, "IS NULL" makes that line always true
def list_problems(
    conn: Connection,
    topic: str | None = None,
    difficulty: str | None = None,
    platform: str | None = None,
) -> list[dict]:
    return conn.execute(
        f"""
        SELECT {PROBLEM_COLUMNS} FROM problems
        WHERE (%(topic)s::text IS NULL OR topic = %(topic)s)
          AND (%(difficulty)s::text IS NULL OR difficulty = %(difficulty)s)
          AND (%(platform)s::text IS NULL OR platform = %(platform)s)
        ORDER BY id
        """,
        {"topic": topic, "difficulty": difficulty, "platform": platform},
    ).fetchall()


def get_problem(conn: Connection, problem_id: int) -> dict | None:
    return conn.execute(
        f"SELECT {PROBLEM_COLUMNS} FROM problems WHERE id = %(id)s",
        {"id": problem_id},
    ).fetchone()


def find_problem_by_title(conn: Connection, title: str, platform: str) -> dict | None:
    return conn.execute(
        f"""
        SELECT {PROBLEM_COLUMNS} FROM problems
        WHERE title = %(title)s AND platform = %(platform)s
        """,
        {"title": title, "platform": platform},
    ).fetchone()


# changes only the columns in "changes", e.g. {"difficulty": "medium"}
def update_problem(conn: Connection, problem_id: int, changes: dict) -> dict | None:
    # column names can't be parameters, so sql.Identifier adds them safely
    # quoted; the values are still parameters (sql.Placeholder)
    assignments = sql.SQL(", ").join(
        sql.SQL("{} = {}").format(sql.Identifier(column), sql.Placeholder(column))
        for column in changes
    )
    query = sql.SQL("UPDATE problems SET {} WHERE id = {} RETURNING {}").format(
        assignments, sql.Placeholder("problem_id"), sql.SQL(PROBLEM_COLUMNS)
    )
    return conn.execute(query, {**changes, "problem_id": problem_id}).fetchone()


# True if a row was deleted, False if there was no problem with that id
def delete_problem(conn: Connection, problem_id: int) -> bool:
    cursor = conn.execute("DELETE FROM problems WHERE id = %(id)s", {"id": problem_id})
    return cursor.rowcount == 1


def create_attempt(conn: Connection, problem_id: int, attempt: dict) -> dict:
    return conn.execute(
        f"""
        INSERT INTO attempts (problem_id, minutes, confidence, solved, notes)
        VALUES (%(problem_id)s, %(minutes)s, %(confidence)s, %(solved)s, %(notes)s)
        RETURNING {ATTEMPT_COLUMNS}
        """,
        {**attempt, "problem_id": problem_id},
    ).fetchone()


# newest first; on the same date, the one saved last comes first
def list_attempts(conn: Connection, problem_id: int) -> list[dict]:
    return conn.execute(
        f"""
        SELECT {ATTEMPT_COLUMNS} FROM attempts
        WHERE problem_id = %(problem_id)s
        ORDER BY created_at DESC, id DESC
        """,
        {"problem_id": problem_id},
    ).fetchall()
