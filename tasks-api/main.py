# the routes: they turn HTTP into calls to services.py and return the right
# status. No product rules here
from contextlib import asynccontextmanager

from fastapi import FastAPI

import errors
from database import connect, create_tables


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
