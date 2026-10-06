from fastapi.testclient import TestClient

from backend.app.main import app


def test_summarize_requires_exactly_one_input() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/summarize",
            data={"summary_length": "standard"},
        )

    assert response.status_code == 400
    assert "exactly one input" in response.json()["detail"].lower()
