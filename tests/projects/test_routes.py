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
    projects = res.json()
    project_ids = {project["id"] for project in projects}

    assert (
        len(projects) == 3
        and first_id in project_ids
        and second_id in project_ids
        and third_id in project_ids
    )


def test_read_project(
    client: TestClient, db: Session, test_data: Iterator[tuple[str, str, str]]
) -> None:
    first_id, _, _ = test_data

    res = client.get(f"/projects/{first_id}/info")

    assert res.json() == {
        "id": first_id,
        "name": "first",
        "description": "The First Project",
    }


def test_read_nonexistent_project(client: TestClient) -> None:
    res = client.get("/projects/123e4567-e89b-12d3-a456-426614174000/info")

    assert res.status_code == 404


def test_create_project(client: TestClient, db: Session) -> None:
    data = {"name": "fourth", "description": "The Fourth project"}

    res = client.post("/projects/", json=data)

    assert ProjectCreate(**res.json()).model_dump() == data


def test_update_project(
    client: TestClient, db: Session, test_data: Iterator[tuple[str, str, str]]
) -> None:
    first_id, _, _ = test_data
    data = {"name": "updated", "description": "Updated project"}

    res = client.put(f"/projects/{first_id}/info", json=data)

    assert ProjectUpdate(**res.json()).model_dump() == data


def test_update_nonexistent_project(client: TestClient) -> None:
    data = {"name": "updated", "description": "Updated project"}

    res = client.put("/projects/not-a-valid-uuid/info", json=data)

    assert res.status_code == 404


def test_delete_project(
    client: TestClient, db: Session, test_data: Iterator[tuple[str, str, str]]
) -> None:
    first_id, _, _ = test_data

    res = client.delete(f"/projects/{first_id}")

    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_delete_nonexistent_project(client: TestClient) -> None:
    res = client.delete("/projects/123e4567-e89b-12d3-a456-426614174000")

    assert res.status_code == 404
