from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.documents import models as doc_models
from src.utils.logger.main import logger


def get_doc_by_id(
    doc_id: UUID, db: Annotated[Session, Depends(get_db)]
) -> doc_models.Document:
    document = (
        db.query(doc_models.Document).filter(doc_models.Document.id == doc_id).first()
    )
    if not document:
        logger.error(document)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return document
