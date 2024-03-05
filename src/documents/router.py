from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.documents import service as doc_service
from src.documents.dependencies import get_doc_by_id, valid_file
from src.projects import models as proj_models
from src.projects.dependencies import get_proj_by_id
from src.users import schemas as user_schemas
from src.users.dependencies import get_curr_user, is_participant

router = APIRouter()


@router.post("/projects/{proj_id}/documents", status_code=status.HTTP_201_CREATED)
def upload_document(
    proj_id: UUID,
    document: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Document:
    url = doc_service.file_upload(document, proj_id)
    return doc_service.create(document.filename, url, proj_id, user, db)


@router.get(
    "/projects/{proj_id}/documents",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def read_documents(
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(5, ge=1, le=10, title="Limit"),
    offset: int = Query(0, ge=0, title="Offset"),
) -> doc_schemas.PaginatedDocuments:
    if not project.documents:
        return doc_schemas.PaginatedDocuments(
            documents=[], count=0, next=None, prev=None
        )
    return doc_service.read_all(project.id, limit, offset, db)


@router.get("/documents/{doc_id}", status_code=status.HTTP_200_OK)
def download(
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    doc = doc_service.read(document, user.id, db)
    return FileResponse(doc.url, filename=doc.name)


@router.put("/documents/{doc_id}", status_code=status.HTTP_200_OK)
def update(
    doc_id: UUID,
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    file: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Document:
    doc = doc_service.update(document, file, user.id, db)
    return doc


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    doc_id: UUID,
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    doc_service.delete(document, user.id, db)
