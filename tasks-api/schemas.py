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
