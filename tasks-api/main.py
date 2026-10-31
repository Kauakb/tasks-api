# the routes: they turn HTTP into calls to services.py and return the right
# status. No product rules here
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Response
from psycopg import Connection

import errors
import services
from database import connect, create_tables, get_db
from schemas import (
    AttemptCreate,
    AttemptRead,
    Difficulty,
    Platform,
    ProblemCreate,
    ProblemRead,
    ProblemUpdate,
)

# each route asks for a connection like this: db: Db
Db = Annotated[Connection, Depends(get_db)]


# runs once when the API starts: makes sure the tables exist
@asynccontextmanager
async def lifespan(app: FastAPI):
    with connect() as conn:
        create_tables(conn)
    yield


app = FastAPI(title="Interview Preparation Tracker", lifespan=lifespan)
errors.register(app)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/problems", response_model=ProblemRead, status_code=201)
def create_problem(data: ProblemCreate, db: Db):
    return services.create_problem(db, data.model_dump())


# the filters come from the URL: /problems?topic=stack&difficulty=easy
@app.get("/problems", response_model=list[ProblemRead])
def list_problems(
    db: Db,
    topic: str | None = None,
    difficulty: Difficulty | None = None,
    platform: Platform | None = None,
):
    return services.list_problems(db, topic, difficulty, platform)


@app.get("/problems/{problem_id}", response_model=ProblemRead)
def get_problem(problem_id: int, db: Db):
    return services.get_problem(db, problem_id)


@app.patch("/problems/{problem_id}", response_model=ProblemRead)
def update_problem(problem_id: int, data: ProblemUpdate, db: Db):
    # exclude_unset: only the fields the client sent
    return services.update_problem(db, problem_id, data.model_dump(exclude_unset=True))


# 204 No Content: success, with an empty body
@app.delete("/problems/{problem_id}", status_code=204)
def delete_problem(problem_id: int, db: Db):
    services.delete_problem(db, problem_id)
    return Response(status_code=204)


@app.post(
    "/problems/{problem_id}/attempts", response_model=AttemptRead, status_code=201
)
def create_attempt(problem_id: int, data: AttemptCreate, db: Db):
    return services.create_attempt(db, problem_id, data.model_dump())


# newest to oldest
@app.get("/problems/{problem_id}/attempts", response_model=list[AttemptRead])
def list_attempts(problem_id: int, db: Db):
    return services.list_attempts(db, problem_id)
