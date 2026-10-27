from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "hello"}


def test_about():
    response = client.get("/about")
    assert response.status_code == 200
    assert response.json() == {"project": "tasks-api", "author": "Kaua B"}
