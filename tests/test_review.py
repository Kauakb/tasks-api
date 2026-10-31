from review import build_queue, urgency


def row(problem_id: int, solved: bool, confidence: int, days: int) -> dict:
    return {
        "id": problem_id,
        "title": f"Problem {problem_id}",
        "platform": "leetcode",
        "topic": "stack",
        "difficulty": "easy",
        "solved": solved,
        "confidence": confidence,
        "days": days,
    }


# the pure functions (no database)


def test_urgency_example_from_the_prd():
    # not solved (+50), confidence 2 (3 x 10 = +30), 4 days ago (+4)
    assert urgency(solved=False, confidence=2, days=4) == 84


def test_urgency_days_are_capped_at_30():
    assert urgency(solved=True, confidence=5, days=45) == 30
    assert urgency(solved=True, confidence=5, days=0) == 0


def test_queue_order_tie_and_limit():
    rows = [
        row(1, solved=True, confidence=4, days=1),  # 0 + 10 + 1 = 11
        row(2, solved=False, confidence=2, days=4),  # 50 + 30 + 4 = 84
        row(3, solved=True, confidence=3, days=0),  # 0 + 20 + 0 = 20
        row(4, solved=True, confidence=4, days=1),  # 11, ties with id 1
    ]
    queue = build_queue(rows, limit=5)
    assert [(item["problem"]["id"], item["score"]) for item in queue] == [
        (2, 84),
        (3, 20),
        (1, 11),
        (4, 11),
    ]
    assert len(build_queue(rows, limit=2)) == 2


def test_queue_without_data():
    assert build_queue([], limit=5) == []


# the endpoint (test database)

PROBLEM = {"platform": "leetcode", "topic": "stack", "difficulty": "easy"}


def add_problem(client, title: str) -> int:
    return client.post("/problems", json={**PROBLEM, "title": title}).json()["id"]


def add_attempt(client, problem_id: int, solved: bool, confidence: int) -> None:
    body = {"minutes": 20, "confidence": confidence, "solved": solved}
    client.post(f"/problems/{problem_id}/attempts", json=body)


def test_review_endpoint(client, db):
    two_sum = add_problem(client, "Two Sum")
    valid = add_problem(client, "Valid Parentheses")
    add_problem(client, "Never tried")  # no attempts: left out of the queue

    add_attempt(client, two_sum, solved=True, confidence=4)
    add_attempt(client, valid, solved=True, confidence=5)
    add_attempt(client, valid, solved=False, confidence=2)  # newest one counts
    # move Valid Parentheses' attempts 4 days into the past
    db.execute(
        "UPDATE attempts SET created_at = CURRENT_DATE - 4 WHERE problem_id = %s",
        (valid,),
    )

    response = client.get("/review")
    assert response.status_code == 200
    assert [(item["problem"]["title"], item["score"]) for item in response.json()] == [
        ("Valid Parentheses", 84),
        ("Two Sum", 10),
    ]
    assert response.json()[0]["problem"] == {
        "id": valid,
        "title": "Valid Parentheses",
        **PROBLEM,
    }


def test_review_limit(client):
    for number in range(3):
        problem_id = add_problem(client, f"Problem {number}")
        add_attempt(client, problem_id, solved=False, confidence=1)
    assert len(client.get("/review").json()) == 3
    assert len(client.get("/review", params={"limit": 2}).json()) == 2


def test_review_invalid_limit(client):
    for limit in (0, 51, "abc"):
        response = client.get("/review", params={"limit": limit})
        assert response.status_code == 422
        assert response.json()["fields"][0]["field"] == "limit"


def test_review_without_data(client):
    response = client.get("/review")
    assert response.status_code == 200
    assert response.json() == []
