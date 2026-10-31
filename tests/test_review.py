from datetime import UTC, datetime, timedelta

from models import Attempt, Problem
from review import build_review_list

NOW = datetime(2026, 10, 31, 12, 0, tzinfo=UTC)


# model objects built in memory: this test never touches the database
def make_problem(problem_id: int, title: str) -> Problem:
    return Problem(
        id=problem_id,
        title=title,
        platform="leetcode",
        topics=["array"],
        difficulty="easy",
    )


def make_attempt(problem_id: int, solved: bool, confidence: int, days_ago: int):
    return Attempt(
        problem_id=problem_id,
        minutes=20,
        confidence=confidence,
        solved=solved,
        created_at=NOW - timedelta(days=days_ago),
    )


# the example from issue #12
def test_review_list_order():
    problems = [
        make_problem(1, "Two Sum"),
        make_problem(2, "Valid Parentheses"),
        make_problem(3, "Merge Intervals"),
        make_problem(4, "Climbing Stairs"),
        make_problem(5, "LRU Cache"),
    ]
    # oldest first, like the endpoint's query
    attempts = [
        make_attempt(3, solved=True, confidence=5, days_ago=45),
        make_attempt(1, solved=False, confidence=1, days_ago=10),
        make_attempt(1, solved=True, confidence=2, days_ago=3),
        make_attempt(4, solved=True, confidence=3, days_ago=2),
        make_attempt(2, solved=False, confidence=2, days_ago=1),
    ]

    result = build_review_list(problems, attempts, NOW)

    titles = [item["problem"].title for item in result]
    assert titles == [
        "Two Sum",  # 40 + 3 (only its newest attempt counts)
        "Valid Parentheses",  # 30 + 1
        "Merge Intervals",  # 10 + 15 (time is capped)
        "Climbing Stairs",  # 20 + 2
        "LRU Cache",  # no attempts: at the bottom
    ]
    assert [item["score"] for item in result] == [43, 31, 25, 22, None]
