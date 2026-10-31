# declarative base is the parent for base, mapped and mapped_column describe colums
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# every model inherits from Base, so base knows all the tables
class Base(DeclarativeBase):
    pass


# one problem object = one row in the "problems" table.
class Problem(Base):
    __tablename__ = "problems"

    # each line means name: Python type = column details
    # mapped[int] and mapped[str] are the type of the colum cause none of them allow none
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    platform: Mapped[str] = mapped_column(String(20))
    topics: Mapped[list[str]] = mapped_column(ARRAY(String(40)))
    difficulty: Mapped[str] = mapped_column(String(10))


# one attempt object = one try at a problem, a row in the "attempts" table
class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    # foreign key: must be the id of a row that exists in problems
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"))
    minutes: Mapped[int]
    confidence: Mapped[int]
    solved: Mapped[bool]
    # "| None" means the column allows empty (NULL) values
    notes: Mapped[str | None] = mapped_column(Text)
    # postgres fills this in with the current date and time when the row is saved
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
