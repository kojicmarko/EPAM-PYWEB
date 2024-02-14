from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_project() -> None:
    data = {"id": 1, "name": "first", "description": "The First project"}
    res = client.get("/projects/1/info")
    assert res.status_code == 200
    assert res.json() == data


def test_create_project() -> None:
    data = {"id": 4, "name": "fourth", "description": "The Fourth project"}
    res = client.post("/projects/", json=data)
    assert res.status_code == 200
    assert res.json() == data


def test_update_project() -> None:
    data = {"id": 3, "name": "third", "description": "The Third project"}
    res = client.put("/projects/3/info", json=data)
    assert res.status_code == 200
    assert res.json() == data


def test_delete_project() -> None:
    data = {"id": 2, "name": "second", "description": "The Second project"}
    res = client.delete("/projects/2")
    assert res.status_code == 200
    assert res.json() == data
