from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.documents import models


def valid_filename(file: UploadFile) -> UploadFile:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file"
        )
    return file


def valid_file(file: Annotated[UploadFile, Depends(valid_filename)]) -> UploadFile:
    if file.content_type not in settings.valid_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type",
        )
    return file


def get_doc_by_id(
    doc_id: UUID, db: Annotated[Session, Depends(get_db)]
) -> models.Document:
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return document
