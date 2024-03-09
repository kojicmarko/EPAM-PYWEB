from typing import Any
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.projects import schemas as proj_schemas
from src.users import schemas as user_schemas
from src.utils.aws.s3 import S3Client
from src.utils.logger.main import logger

s3 = S3Client()


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


def read(document: doc_models.Document) -> Any:
    doc = doc_schemas.Document.model_validate(document)
    res = s3.download(f"{doc.project_id}_{doc.name}", "documents")
    return res


def create(
    doc_file: UploadFile,
    project: proj_schemas.Project,
    user: user_schemas.User,
    db: Session,
) -> doc_schemas.Document:
    url = s3.upload(doc_file, project.id, "documents")

    document = doc_models.Document(
        name=str(doc_file.filename), url=url, owner_id=user.id, project_id=project.id
    )

    db.add(document)
    db.commit()

    return doc_schemas.Document.model_validate(document)


def update(
    document: doc_models.Document, file: UploadFile, db: Session
) -> doc_schemas.Document:
    s3.delete(f"{document.project_id}_{document.name}", "documents")

    document.name = str(file.filename)
    document.url = s3.upload(file, document.project_id, "documents")
    db.commit()

    return doc_schemas.Document.model_validate(document)


def delete(
    document: doc_models.Document,
    curr_user_id: UUID,
    owner_id: UUID,
    db: Session,
) -> None:
    if owner_id != curr_user_id:
        log_msg = "Current User: %s - IS NOT OWNER - Owner: %s"
        logger.error(log_msg, curr_user_id, owner_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Project owner can delete Documents",
        )

    s3.delete(f"{document.project_id}_{document.name}", "documents")
    db.delete(document)
    db.commit()
