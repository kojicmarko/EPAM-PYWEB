from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.files import service as file_service
from src.users import schemas as user_schemas


def read_all(
    proj_id: UUID, limit: int, offset: int, db: Session
) -> doc_schemas.PaginatedDocuments:
    count = db.query(func.count(doc_models.Document.id)).scalar()
    doc_list = (
        db.query(doc_models.Document)
        .filter(doc_models.Document.project_id == proj_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    documents = [doc_schemas.Document.model_validate(doc) for doc in doc_list]
    next_offset = offset + limit if offset + limit < count else None
    prev_offset = max(0, offset - limit) if offset > 0 else None
    return doc_schemas.PaginatedDocuments(
        documents=documents, count=count, next=next_offset, prev=prev_offset
    )


def read(document: doc_models.Document) -> doc_schemas.Document:
    return doc_schemas.Document.model_validate(document)


def create(
    name: str | None, url: str, proj_id: UUID, user: user_schemas.User, db: Session
) -> doc_schemas.Document:
    document = doc_models.Document(
        name=name, url=url, owner_id=user.id, project_id=proj_id
    )
    db.add(document)
    db.commit()
    return doc_schemas.Document.model_validate(document)


def update(
    document: doc_models.Document, file: UploadFile, user_id: UUID, db: Session
) -> doc_schemas.Document:
    old_url = document.url
    new_url = file_service.upload(file, document.project_id)

    document.url = new_url
    db.commit()

    file_service.delete(old_url)

    return doc_schemas.Document.model_validate(document)


def delete(
    document: doc_models.Document,
    user_id: UUID,
    owner_id: UUID,
    db: Session,
) -> None:
    if owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden access"
        )

    file_service.delete(document.url)
    db.delete(document)
    db.commit()
