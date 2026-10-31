from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

import errors
from services import ConflictError, NotFoundError


# a small app with one route per error type, using the real error handlers
def make_client() -> TestClient:
    app = FastAPI()
    errors.register(app)

    class Body(BaseModel):
        confidence: int = Field(ge=1, le=5)

    @app.get("/not-found")
    def raise_not_found():
        raise NotFoundError("Problem 99 not found")

    @app.get("/conflict")
    def raise_conflict():
        raise ConflictError("Problem 'Two Sum' already exists on leetcode")

    @app.post("/validate")
    def validate(body: Body):
        return body

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret detail")

    # raise_server_exceptions=False: get the 500 response instead of the exception
    return TestClient(app, raise_server_exceptions=False)


def test_not_found_error():
    response = make_client().get("/not-found")
    assert response.status_code == 404
    assert response.json() == {"error": "NOT_FOUND", "message": "Problem 99 not found"}


def test_conflict_error():
    response = make_client().get("/conflict")
    assert response.status_code == 409
    assert response.json() == {
        "error": "CONFLICT",
        "message": "Problem 'Two Sum' already exists on leetcode",
    }


def test_validation_error_lists_fields():
    response = make_client().post("/validate", json={"confidence": 9})
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert body["message"] == "Request validation failed"
    assert body["fields"][0]["field"] == "confidence"


def test_malformed_json():
    response = make_client().post(
        "/validate", content="{bad json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json()["fields"][0]["field"] == "body"


def test_unknown_route():
    response = make_client().get("/nope")
    assert response.status_code == 404
    assert response.json() == {"error": "NOT_FOUND", "message": "Route /nope not found"}


def test_method_not_allowed():
    response = make_client().delete("/not-found")
    assert response.status_code == 405
    assert response.json()["error"] == "METHOD_NOT_ALLOWED"


def test_unexpected_error_hides_details():
    response = make_client().get("/boom")
    assert response.status_code == 500
    assert response.json() == {
        "error": "INTERNAL_ERROR",
        "message": "Internal server error",
    }
