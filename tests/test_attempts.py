from datetime import date

import pytest

PROBLEM = {
    "title": "Valid Parentheses",
    "platform": "leetcode",
    "topic": "stack",
    "difficulty": "easy",
}
ATTEMPT = {
    "minutes": 25,
    "confidence": 2,
    "solved": False,
    "notes": "Forgot the empty stack",
}


@pytest.fixture
def problem_id(client):
    return client.post("/problems", json=PROBLEM).json()["id"]


# US-09 log an attempt


def test_create_attempt(client, problem_id):
    response = client.post(f"/problems/{problem_id}/attempts", json=ATTEMPT)
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "problem_id": problem_id,
        **ATTEMPT,
        "created_at": date.today().isoformat(),
    }


def test_notes_are_optional(client, problem_id):
    body = {key: value for key, value in ATTEMPT.items() if key != "notes"}
    response = client.post(f"/problems/{problem_id}/attempts", json=body)
    assert response.status_code == 201
    assert response.json()["notes"] == ""


@pytest.mark.parametrize(
    "change",
    [
        {"minutes": 0},
        {"minutes": -5},
        {"minutes": 601},
        {"confidence": 0},
        {"confidence": 6},
        {"solved": "yes"},
        {"notes": "x" * 501},
    ],
)
def test_invalid_attempt_fields(client, problem_id, change):
    response = client.post(
        f"/problems/{problem_id}/attempts", json={**ATTEMPT, **change}
    )
    assert response.status_code == 422
    assert response.json()["fields"][0]["field"] == next(iter(change))


def test_attempt_on_missing_problem(client):
    response = client.post("/problems/99/attempts", json=ATTEMPT)
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


# US-10 attempt history


def test_history_newest_first(client, problem_id):
    for minutes in (10, 20, 30):
        client.post(
            f"/problems/{problem_id}/attempts", json={**ATTEMPT, "minutes": minutes}
        )
    response = client.get(f"/problems/{problem_id}/attempts")
    assert response.status_code == 200
    assert [attempt["minutes"] for attempt in response.json()] == [30, 20, 10]


def test_history_without_attempts(client, problem_id):
    response = client.get(f"/problems/{problem_id}/attempts")
    assert response.status_code == 200
    assert response.json() == []


def test_history_of_missing_problem(client):
    assert client.get("/problems/99/attempts").status_code == 404
