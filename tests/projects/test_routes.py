from typing import Iterator

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.projects.schemas import ProjectCreate, ProjectUpdate


def test_read_projects(
    client: TestClient, db: Session, test_data: Iterator[tuple[str, str, str]]
) -> None:
    first_id, second_id, third_id = test_data

    res = client.get("/projects/")
    assert res.status_code == 200
    projects = res.json()

    assert isinstance(projects, list)
    assert len(projects) == 3

    # Check that the list contains the projects we created
    project_ids = {project["id"] for project in projects}
    assert first_id in project_ids
    assert second_id in project_ids
    assert third_id in project_ids


def test_read_project(
    client: TestClient, db: Session, test_data: Iterator[tuple[str, str, str]]
) -> None:
    first_id, second_id, third_id = test_data

    data = {"id": first_id, "name": "first", "description": "The First Project"}
    res = client.get(f"/projects/{first_id}/info")
    assert res.status_code == 200
    assert res.json() == data


def test_read_nonexistent_project(client: TestClient) -> None:
    res = client.get("/projects/123e4567-e89b-12d3-a456-426614174000/info")
    assert res.status_code == 404
    res = client.get("/projects/not-a-valid-uuid/info")
    assert res.status_code == 404


def test_create_project(client: TestClient, db: Session) -> None:
    data = {"name": "fourth", "description": "The Fourth project"}
    res = client.post("/projects/", json=data)
    assert res.status_code == status.HTTP_201_CREATED
    project = ProjectCreate(**res.json())
    assert project.name == data["name"]
    assert project.description == data["description"]


def test_update_project(
    client: TestClient, db: Session, test_data: Iterator[tuple[str, str, str]]
) -> None:
    first_id, _, _ = test_data
    data = {"name": "updated", "description": "Updated project"}
    res = client.put(f"/projects/{first_id}/info", json=data)
    assert res.status_code == status.HTTP_200_OK
    project = ProjectUpdate(**res.json())
    assert project.name == data["name"]
    assert project.description == data["description"]


def test_update_nonexistent_project(client: TestClient) -> None:
    data = {"name": "updated", "description": "Updated project"}
    res = client.put("/projects/123e4567-e89b-12d3-a456-426614174000/info", json=data)
    assert res.status_code == 404
    res = client.put("/projects/not-a-valid-uuid/info", json=data)
    assert res.status_code == 404


def test_delete_project(
    client: TestClient, db: Session, test_data: Iterator[tuple[str, str, str]]
) -> None:
    first_id, _, _ = test_data
    res = client.delete(f"/projects/{first_id}")
    assert res.status_code == status.HTTP_204_NO_CONTENT
    res = client.get(f"/projects/{first_id}/info")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_project(client: TestClient) -> None:
    res = client.delete("/projects/123e4567-e89b-12d3-a456-426614174000")
    assert res.status_code == 404
    res = client.delete("/projects/not-a-valid-uuid")
    assert res.status_code == 404
