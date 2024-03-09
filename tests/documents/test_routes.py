from io import BytesIO

from fastapi import UploadFile, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.documents import schemas as doc_schemas
from src.projects.schemas import Project
from src.users.schemas import User
from src.utils.aws.s3 import S3Client

s3 = S3Client()


def test_read_project_documents(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_documents: list[doc_schemas.Document],
    test_token: str,
) -> None:
    project = test_projects[0]
    limit = 1
    offset = 2

    res = client.get(
        f"/projects/{project.id}/documents?limit={limit}&offset={offset}",
        headers={"MyAuthorization": f"Bearer {test_token}"},
    )

    expected_documents = test_documents[offset : offset + limit]
    assert len(res.json()["documents"]) == len(expected_documents)


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
    expected_end_of_url = f"documents/{project.id}_mock_file.pdf"

    res = client.post(
        f"/projects/{project.id}/documents",
        headers={"MyAuthorization": f"Bearer {test_token}"},
        files=data,
    )

    s3.delete(f"{project.id}_mock_file.pdf", "documents")

    assert res.json()["url"].endswith(expected_end_of_url)


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
        headers={"MyAuthorization": f"Bearer {test_token}"},
        files=data,
    )

    assert res.status_code == 422


def test_download_document(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
    mock_upload_file: UploadFile,
    test_documents: list[doc_schemas.Document],
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
    test_documents: list[doc_schemas.Document],
) -> None:
    project = test_projects[0]
    document = test_documents[0]

    data = {
        "file": ("mock_file.pdf", mock_upload_file.file, mock_upload_file.content_type)
    }
    expected_end_of_url = f"documents/{project.id}_mock_file.pdf"

    res = client.put(
        f"/documents/{document.id}/",
        headers={"MyAuthorization": f"Bearer {test_token}"},
        files=data,
    )

    s3.delete(f"{project.id}_mock_file.pdf", "documents")

    assert res.json()["url"].endswith(expected_end_of_url)


def test_delete_document(
    client: TestClient,
    db: Session,
    test_user: User,
    test_projects: list[Project],
    test_token: str,
    mock_upload_file: UploadFile,
    test_documents: list[doc_schemas.Document],
) -> None:
    document = test_documents[0]

    res = client.delete(
        f"/documents/{document.id}", headers={"MyAuthorization": f"Bearer {test_token}"}
    )

    assert res.status_code == status.HTTP_204_NO_CONTENT
