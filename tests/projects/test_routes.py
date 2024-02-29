import os
from io import BytesIO

from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.projects.schemas import Project
from src.users.schemas import User


def test_read_projects(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
) -> None:
    res = client.get("/projects/", headers={"Authorization": f"Bearer {test_token}"})

    assert res.json() == [
        {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "owner_id": str(project.owner_id),
            "logo_id": project.logo_id,
        }
        for project in test_projects
    ]


def test_read_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
) -> None:
    project = test_projects[0]

    res = client.get(
        f"/projects/{project.id}/info",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert res.json() == {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "owner_id": str(project.owner_id),
        "logo_id": project.logo_id,
    }


def test_read_nonexistent_project(
    client: TestClient,
    test_user: User,
    test_token: str,
) -> None:
    res = client.get(
        "/projects/bc3f2dac-4915-4144-979e-569b8cc77534/info",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert res.status_code == 404


def test_unauthorized_project_access(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    unauthorized_token: str,
) -> None:
    project = test_projects[0]

    res = client.get(
        f"/projects/{project.id}/info",
        headers={"Authorization": f"Bearer {unauthorized_token}"},
    )

    assert res.status_code == 404


def test_create_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_token: str,
) -> None:
    data = {"name": "project9999"}

    res = client.post(
        "/projects/", json=data, headers={"Authorization": f"Bearer {test_token}"}
    )

    assert res.json()["name"] == data["name"] and res.json()["owner_id"] == str(
        test_user.id
    )


def test_update_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
) -> None:
    project = test_projects[0]
    data = {"name": "updated_project"}

    res = client.put(
        f"/projects/{project.id}/info",
        json=data,
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert res.json()["name"] == data["name"]


def test_update_nonexistent_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_token: str,
) -> None:
    data = {"name": "updated_project"}

    res = client.put(
        "/projects/bc3f2dac-4915-4144-979e-569b8cc77534/info",
        json=data,
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert res.status_code == 404


def test_delete_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
) -> None:
    project = test_projects[0]

    res = client.delete(
        f"/projects/{project.id}", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert res.status_code == 204


def test_delete_nonexistent_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_token: str,
) -> None:
    res = client.delete(
        "/projects/bc3f2dac-4915-4144-979e-569b8cc77534/",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert res.status_code == 404


def test_user_cannot_delete_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    participant_token: str,
) -> None:
    project = test_projects[0]

    res = client.delete(
        f"/projects/{project.id}",
        headers={"Authorization": f"Bearer {participant_token}"},
    )

    assert res.status_code == 404


def test_invite_to_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
    invited_user: User,
) -> None:
    project = test_projects[0]

    res = client.post(
        f"/projects/{project.id}/invite?user={invited_user.username}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert res.status_code == 201


def test_user_cannot_invite_to_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    participant_token: str,
    invited_user: User,
) -> None:
    project = test_projects[0]

    res = client.post(
        f"/projects/{project.id}/invite?user={invited_user.username}",
        headers={"Authorization": f"Bearer {participant_token}"},
    )

    assert res.status_code == 403


def test_upload_document_to_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
    mock_upload_file: UploadFile,
) -> None:
    project = test_projects[0]

    data = {
        "file": ("mock_file.pdf", mock_upload_file.file, mock_upload_file.content_type)
    }

    res = client.post(
        f"/projects/{project.id}/documents",
        headers={"Authorization": f"Bearer {test_token}"},
        files=data,
    )

    expected_end_of_path = os.path.join(
        "bucket", "documents", f"{project.id}_mock_file.pdf"
    )

    assert res.json()["url"].endswith(expected_end_of_path)


def test_upload_unsupported_document_to_project(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
) -> None:
    project = test_projects[0]

    mock_file = BytesIO(b"file content")
    mock_file.name = "mock_file.txt"
    upload_file = UploadFile(file=mock_file)

    data = {"file": ("mock_file.txt", upload_file.file, upload_file.content_type)}

    res = client.post(
        f"/projects/{project.id}/documents",
        headers={"Authorization": f"Bearer {test_token}"},
        files=data,
    )

    assert res.status_code == 422
