# shared setup for all tests (pytest loads this file automatically)
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# tests use their own database, never the development one.
# load_dotenv reads .env but doesn't override variables already set (as in CI)
load_dotenv()
os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

# these imports read DATABASE_URL, so they must come after the line above
from database import connect, create_tables
from main import app


# a connection to the test database, with empty tables and ids starting at 1
@pytest.fixture
def db():
    with connect() as conn:
        create_tables(conn)
        conn.execute("TRUNCATE problems, attempts RESTART IDENTITY")
        yield conn


# calls the API in memory; "with" also runs the startup code (lifespan)
@pytest.fixture
def client(db):
    with TestClient(app) as client:
        yield client
