import pytest
from fastapi.testclient import TestClient

from app import services
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Use a throwaway data folder so tests never touch real user data."""
    data_dir = tmp_path / "data"
    monkeypatch.setattr(services, "datafolder", str(data_dir))
    monkeypatch.setattr(services, "datasource", str(data_dir / "users.json"))
    return TestClient(app)


def test_index_returns_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_users_starts_empty(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == {"data": []}


def test_create_user_then_list_it(client):
    payload = {"first_name": "Ada", "last_name": "Lovelace", "age": 36}
    created = client.post("/users", json=payload)
    assert created.status_code == 200
    assert created.json() == {"success": True}

    listed = client.get("/users").json()
    assert listed["data"] == [payload]


def test_create_user_rejects_bad_input(client):
    response = client.post("/users", json={"first_name": "Only"})
    assert response.status_code == 422


def test_metrics_endpoint_exposes_prometheus_format(client):
    client.get("/")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
