from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Attempt, Problem
from review import build_review_list
from schemas import (
    AttemptCreate,
    AttemptRead,
    ProblemCreate,
    ProblemRead,
    ReviewItem,
)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "hello"}


@app.get("/about")
def about():
    return {"project": "tasks-api", "author": "Kaua B"}


# this runs the function when post request
@app.post("/problems", response_model=ProblemRead, status_code=201)
def create_problem(data: ProblemCreate, db: Annotated[Session, Depends(get_db)]):
    # model dump turns a schema into a dict: {title: two sum, platform, leetcode}
    problem = Problem(**data.model_dump())
    # this tells the sessions that we want to save it / nothing goes to DB yet
    db.add(problem)
    # now the insert actually runs and saved. postgre creates the id
    db.commit()
    # reloads the row from the db, so problem.id has the new value
    db.refresh(problem)
    # the return below return the sqlalchemy object, and problemRead turns into JSON with the id included
    return problem


# returns every problem as a JSON list
@app.get("/problems", response_model=list[ProblemRead])
def list_problems(db: Annotated[Session, Depends(get_db)]):
    # select builds the query (SELECT * FROM problems ORDER BY id)
    # order_by keeps the list in the same order every time
    query = select(Problem).order_by(Problem.id)
    # scalars runs it and gives back Problem objects, all() puts them in a list
    return db.scalars(query).all()


# stops the request with a 404 error when the problem doesn't exist
def get_problem_or_404(db: Session, problem_id: int) -> Problem:
    # db.get looks up one row by its primary key, None if there's no such row
    problem = db.get(Problem, problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


# {problem_id} in the URL becomes the problem_id parameter, e.g. /problems/3/attempts
@app.post(
    "/problems/{problem_id}/attempts", response_model=AttemptRead, status_code=201
)
def create_attempt(
    problem_id: int, data: AttemptCreate, db: Annotated[Session, Depends(get_db)]
):
    get_problem_or_404(db, problem_id)
    # the body has the attempt fields, the URL gives the problem it belongs to
    attempt = Attempt(**data.model_dump(), problem_id=problem_id)
    db.add(attempt)
    db.commit()
    # reloads id and created_at, which the database filled in
    db.refresh(attempt)
    return attempt


# returns every attempt at one problem, oldest first
@app.get("/problems/{problem_id}/attempts", response_model=list[AttemptRead])
def list_attempts(problem_id: int, db: Annotated[Session, Depends(get_db)]):
    get_problem_or_404(db, problem_id)
    # where filters the rows: SELECT * FROM attempts WHERE problem_id = ...
    query = (
        select(Attempt)
        .where(Attempt.problem_id == problem_id)
        .order_by(Attempt.created_at, Attempt.id)
    )
    return db.scalars(query).all()


# every problem, from most to least urgent to review (formula in review.py)
@app.get("/review", response_model=list[ReviewItem])
def review_list(db: Annotated[Session, Depends(get_db)]):
    problems = db.scalars(select(Problem)).all()
    # oldest first, so build_review_list keeps the newest attempt per problem
    query = select(Attempt).order_by(Attempt.created_at, Attempt.id)
    attempts = db.scalars(query).all()
    return build_review_list(problems, attempts, datetime.now(UTC))
