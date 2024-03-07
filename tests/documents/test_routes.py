import os

from fastapi import UploadFile, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.documents.schemas import Document
from src.projects.schemas import Project
from src.users.schemas import User


def test_download_document(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
    mock_upload_file: UploadFile,
    test_documents: list[Document],
) -> None:
    document = test_documents[0]

    res = client.get(
        f"/documents/{document.id}/",
        headers={"MyAuthorization": f"Bearer {test_token}"},
    )

    assert res.status_code == 200


def test_update_document(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
    mock_upload_file: UploadFile,
    test_documents: list[Document],
) -> None:
    project = test_projects[0]
    document = test_documents[0]

    data = {
        "file": ("mock_file.pdf", mock_upload_file.file, mock_upload_file.content_type)
    }

    res = client.put(
        f"/documents/{document.id}/",
        headers={"MyAuthorization": f"Bearer {test_token}"},
        files=data,
    )

    expected_end_of_path = os.path.join(
        "bucket", "documents", f"{project.id}_mock_file.pdf"
    )

    assert res.json()["url"].endswith(expected_end_of_path)


def test_delete_document(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
    mock_upload_file: UploadFile,
    test_documents: list[Document],
) -> None:
    document = test_documents[0]

    res = client.delete(
        f"/documents/{document.id}", headers={"MyAuthorization": f"Bearer {test_token}"}
    )

    assert res.status_code == status.HTTP_204_NO_CONTENT
