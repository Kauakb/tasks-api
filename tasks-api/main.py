from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import get_db
from models import Problem
from schemas import ProblemCreate, ProblemRead

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
