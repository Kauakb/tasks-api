# declarative base is the parent for base, mapped and mapped_column describe colums
from sqlalchemy import String
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
