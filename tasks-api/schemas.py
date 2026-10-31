from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# a title is trimmed first, then must be 1 to 120 characters
Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
Topic = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=2, max_length=40)
]


# what the client send to create a problem(no id; the database makes it)
class ProblemCreate(BaseModel):
    title: Title
    platform: Literal["leetcode", "hackerrank", "codesignal", "other"]
    topics: Annotated[list[Topic], Field(min_length=1)]
    difficulty: Literal["easy", "medium", "hard"]


# what API sends back: same fields plus the id from the database
class ProblemRead(ProblemCreate):  # inherits from problem create
    model_config = ConfigDict(from_attributes=True)

    id: int


# what the client sends to log an attempt
# (no problem_id: it comes from the URL; no created_at: the database sets it)
class AttemptCreate(BaseModel):
    minutes: Annotated[int, Field(gt=0)]  # gt = greater than
    confidence: Annotated[int, Field(ge=1, le=5)]  # ge/le = from 1 to 5
    solved: bool
    notes: str | None = None  # optional: leave it out and it's None


# what the API sends back: the same fields plus what the server filled in
class AttemptRead(AttemptCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    created_at: datetime


# one line of the review list (score and last_attempt_at are None
# for a problem with no attempts yet)
class ReviewItem(BaseModel):
    problem: ProblemRead
    score: int | None
    last_attempt_at: datetime | None
