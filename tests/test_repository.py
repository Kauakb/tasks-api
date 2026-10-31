import psycopg
import pytest

import repository
from database import connect

TWO_SUM = {
    "title": "Two Sum",
    "platform": "leetcode",
    "topic": "hashmap",
    "difficulty": "easy",
}
ATTEMPT = {"minutes": 20, "confidence": 3, "solved": True, "notes": ""}


def test_problem_is_still_there_with_a_new_connection(db):
    created = repository.create_problem(db, TWO_SUM)
    # a new connection is like restarting the API
    with connect() as other:
        assert repository.get_problem(other, created["id"]) == created


def test_deleting_a_problem_deletes_its_attempts(db):
    problem = repository.create_problem(db, TWO_SUM)
    repository.create_attempt(db, problem["id"], ATTEMPT)

    assert repository.delete_problem(db, problem["id"]) is True
    assert repository.list_attempts(db, problem["id"]) == []


def test_same_title_on_same_platform_is_refused(db):
    repository.create_problem(db, TWO_SUM)
    with pytest.raises(psycopg.errors.UniqueViolation):
        repository.create_problem(db, TWO_SUM)


def test_list_problems_with_filters(db):
    repository.create_problem(db, TWO_SUM)
    repository.create_problem(
        db, {**TWO_SUM, "title": "Valid Parentheses", "topic": "stack"}
    )

    stack = repository.list_problems(db, topic="stack")
    assert [p["title"] for p in stack] == ["Valid Parentheses"]
    assert len(repository.list_problems(db)) == 2


def test_update_changes_only_the_given_fields(db):
    problem = repository.create_problem(db, TWO_SUM)
    updated = repository.update_problem(db, problem["id"], {"difficulty": "medium"})
    assert updated == {**problem, "difficulty": "medium"}
