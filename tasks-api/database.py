# the connection to PostgreSQL, using the psycopg driver (no ORM:
# all the SQL is written by hand in repository.py)
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from config import settings

SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def connect() -> psycopg.Connection:
    # autocommit: each SQL statement is saved as soon as it runs
    # dict_row: each row comes back as a dict, e.g. {"id": 1, "title": "Two Sum"}
    return psycopg.connect(settings.database_url, autocommit=True, row_factory=dict_row)


# creates the tables that don't exist yet (runs when the API starts)
def create_tables(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA_FILE.read_text(encoding="utf-8"))


# gives each request its own connection, and closes it when the request ends
def get_db():
    with connect() as conn:
        yield conn
