import os
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).parents[1] / "tasks-api"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_page(client):
    assert client.get("/docs").status_code == 200


def test_api_stops_without_database_url(tmp_path):
    # imports config in an empty folder (no .env) with DATABASE_URL unset
    env = {key: value for key, value in os.environ.items() if key != "DATABASE_URL"}
    env["PYTHONPATH"] = str(APP_DIR)
    result = subprocess.run(
        [sys.executable, "-c", "import config"],
        # check=False: a failing exit code is what this test expects
        check=False,
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Missing environment variable: DATABASE_URL" in result.stderr
