from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.documents import service as doc_service
from src.documents.dependencies import get_doc_by_id, valid_file
from src.users import schemas as user_schemas

# from src.projects import service as project_service
from src.users.dependencies import get_curr_user

router = APIRouter(prefix="/documents")


@router.get("/{doc_id}", status_code=status.HTTP_200_OK)
def download(
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    doc = doc_service.read(document, user.id, db)
    return FileResponse(doc.url, filename=doc.name)


@router.put("/{doc_id}", status_code=status.HTTP_200_OK)
def update(
    doc_id: UUID,
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    file: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Document:
    doc = doc_service.update(document, file, user.id, db)
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    doc_id: UUID,
    document: Annotated[doc_models.Document, Depends(get_doc_by_id)],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    doc_service.delete(document, user.id, db)
