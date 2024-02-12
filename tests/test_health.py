from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_health() -> None:
    data = {"status": "It's ALIVE!"}
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == data
