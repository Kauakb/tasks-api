VALID = {
    "title": "Valid Parentheses",
    "platform": "leetcode",
    "topic": "stack",
    "difficulty": "easy",
}
TWO_SUM = {
    "title": "Two Sum",
    "platform": "leetcode",
    "topic": "hashmap",
    "difficulty": "easy",
}


def field_names(response) -> list[str]:
    return [field["field"] for field in response.json()["fields"]]


# US-04 create


def test_create_problem(client):
    response = client.post("/problems", json=VALID)
    assert response.status_code == 201
    assert response.json() == {"id": 1, **VALID}


def test_create_trims_title_and_lowercases_topic(client):
    body = {**VALID, "title": "  Valid Parentheses  ", "topic": " Stack "}
    response = client.post("/problems", json=body)
    assert response.json()["title"] == "Valid Parentheses"
    assert response.json()["topic"] == "stack"


def test_create_invalid_fields(client):
    body = {"title": "   ", "platform": "codewars", "difficulty": "impossible"}
    response = client.post("/problems", json=body)
    assert response.status_code == 422
    assert set(field_names(response)) == {"title", "platform", "topic", "difficulty"}


def test_create_duplicate_title_on_same_platform(client):
    client.post("/problems", json=VALID)
    response = client.post("/problems", json=VALID)
    assert response.status_code == 409
    assert response.json() == {
        "error": "CONFLICT",
        "message": "Problem 'Valid Parentheses' already exists on leetcode",
    }


def test_same_title_on_another_platform_is_allowed(client):
    client.post("/problems", json=VALID)
    response = client.post("/problems", json={**VALID, "platform": "hackerrank"})
    assert response.status_code == 201


# US-05 list and filter


def test_list_empty(client):
    response = client.get("/problems")
    assert response.status_code == 200
    assert response.json() == []


def test_list_ordered_by_id_with_filters(client):
    client.post("/problems", json=VALID)
    client.post("/problems", json=TWO_SUM)
    client.post("/problems", json={**TWO_SUM, "title": "Min Stack", "topic": "stack"})

    all_titles = [p["title"] for p in client.get("/problems").json()]
    assert all_titles == ["Valid Parentheses", "Two Sum", "Min Stack"]

    stack = client.get("/problems", params={"topic": "stack"}).json()
    assert [p["id"] for p in stack] == [1, 3]

    combined = client.get("/problems", params={"topic": "stack", "difficulty": "easy"})
    assert [p["id"] for p in combined.json()] == [1, 3]


def test_list_invalid_filter(client):
    response = client.get("/problems", params={"difficulty": "impossible"})
    assert response.status_code == 422
    assert field_names(response) == ["difficulty"]


# US-06 get one


def test_get_problem(client):
    client.post("/problems", json=VALID)
    response = client.get("/problems/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Valid Parentheses"


def test_get_missing_problem(client):
    response = client.get("/problems/99")
    assert response.status_code == 404
    assert response.json() == {"error": "NOT_FOUND", "message": "Problem 99 not found"}


def test_get_problem_with_invalid_id(client):
    response = client.get("/problems/abc")
    assert response.status_code == 422
    assert field_names(response) == ["problem_id"]


# US-07 edit


def test_update_one_field(client):
    client.post("/problems", json=VALID)
    response = client.patch("/problems/1", json={"difficulty": "medium"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, **VALID, "difficulty": "medium"}


def test_update_several_fields(client):
    client.post("/problems", json=VALID)
    response = client.patch("/problems/1", json={"topic": "Strings", "title": "VP"})
    assert response.json() == {"id": 1, **VALID, "topic": "strings", "title": "VP"}


def test_update_empty_body(client):
    client.post("/problems", json=VALID)
    assert client.patch("/problems/1", json={}).status_code == 422


def test_update_invalid_field(client):
    client.post("/problems", json=VALID)
    assert client.patch("/problems/1", json={"difficulty": "x"}).status_code == 422
    assert client.patch("/problems/1", json={"title": None}).status_code == 422


def test_update_missing_problem(client):
    response = client.patch("/problems/99", json={"difficulty": "medium"})
    assert response.status_code == 404


def test_update_to_a_duplicate_title(client):
    client.post("/problems", json=VALID)
    client.post("/problems", json=TWO_SUM)
    response = client.patch("/problems/2", json={"title": "Valid Parentheses"})
    assert response.status_code == 409


# US-08 delete


def test_delete_problem(client):
    client.post("/problems", json=VALID)
    response = client.delete("/problems/1")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/problems/1").status_code == 404


def test_delete_missing_problem(client):
    assert client.delete("/problems/99").status_code == 404


def test_method_not_allowed_on_problems(client):
    response = client.delete("/problems")
    assert response.status_code == 405
    assert response.json()["error"] == "METHOD_NOT_ALLOWED"
