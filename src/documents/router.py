from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.documents import service as doc_service
from src.documents.dependencies import get_doc_by_id
from src.files.dependencies import valid_file
from src.projects import models as proj_models
from src.projects import schemas as proj_schemas
from src.projects.dependencies import get_proj_by_id
from src.users import schemas as user_schemas
from src.users.dependencies import get_curr_user, is_participant
from src.utils.logger.main import logger

router = APIRouter()


@router.post("/projects/{proj_id}/documents", status_code=status.HTTP_201_CREATED)
def upload_document(
    proj_model: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    document: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Document:
    log_msg = "User: %s, Uploaded: %s to Project: %s"
    logger.warning(log_msg, user.username, document, proj_model.name)
    project = proj_schemas.Project.model_validate(proj_model)
    return doc_service.create(document, project, user, db)


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
def download_document(
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    curr_user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Document:
    is_participant(document.project_id, curr_user, db)
    return doc_service.read(document)


@router.put("/documents/{doc_id}", status_code=status.HTTP_200_OK)
def update_document(
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    file: Annotated[UploadFile, Depends(valid_file)],
    curr_user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Document:
    is_participant(document.project_id, curr_user, db)
    log_msg = "Updated Document: %s to Document: %s"
    logger.warning(log_msg, document, file)
    return doc_service.update(document, file, db)


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    curr_user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    project = get_proj_by_id(document.project_id, db)
    doc_service.delete(document, curr_user.id, project.owner_id, db)
