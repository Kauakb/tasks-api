# what JSON the API accepts and returns. Pydantic checks every request
# against these rules; a broken rule becomes a 422 VALIDATION_ERROR
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StrictBool, StringConstraints, model_validator

Platform = Literal["leetcode", "codesignal", "hackerrank", "other"]
Difficulty = Literal["easy", "medium", "hard"]

# trimmed first, then 1 to 120 characters
Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
# trimmed and lowercased, e.g. " Stack " -> "stack"
Topic = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, min_length=1, max_length=40
    ),
]


# what the client sends to create a problem (no id: the database makes it)
class ProblemCreate(BaseModel):
    title: Title
    platform: Platform
    topic: Topic
    difficulty: Difficulty


# PATCH: every field is optional, but at least one must be sent
class ProblemUpdate(BaseModel):
    title: Title | None = None
    platform: Platform | None = None
    topic: Topic | None = None
    difficulty: Difficulty | None = None

    @model_validator(mode="after")
    def check_fields(self):
        # model_fields_set = the fields the client actually sent
        if not self.model_fields_set:
            raise ValueError("send at least one field to change")
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} can't be null")
        return self


# what the API sends back
class ProblemRead(BaseModel):
    id: int
    title: str
    platform: str
    topic: str
    difficulty: str


# what the client sends to log an attempt
# (no problem_id: it comes from the URL; no created_at: the database sets it)
class AttemptCreate(BaseModel):
    minutes: Annotated[int, Field(gt=0, le=600)]  # more than 0, at most 600
    confidence: Annotated[int, Field(ge=1, le=5)]  # from 1 to 5
    # StrictBool: only true/false, not "yes" or 1
    solved: StrictBool
    notes: Annotated[str, StringConstraints(max_length=500)] = ""


class AttemptRead(BaseModel):
    id: int
    problem_id: int
    minutes: int
    confidence: int
    solved: bool
    notes: str
    created_at: date  # sent as "YYYY-MM-DD"


# one item of the review queue
class ReviewItem(BaseModel):
    problem: ProblemRead
    score: int
