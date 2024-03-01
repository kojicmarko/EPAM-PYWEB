import os
import pathlib
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.models import ProjectUser
from src.projects.dependencies import get_proj_by_id
from src.users import schemas as user_schemas


def read(
    document: doc_models.Document, user_id: UUID, db: Session
) -> doc_schemas.Document:
    project_user = db.query(
        exists().where(
            ProjectUser.user_id == user_id,
            ProjectUser.project_id == document.project_id,
        )
    ).scalar()

    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden access"
        )

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
    project_user = db.query(
        exists().where(
            ProjectUser.user_id == user_id,
            ProjectUser.project_id == document.project_id,
        )
    ).scalar()

    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden access"
        )
    if file.filename is not None:
        document.name = file.filename

    old_url = document.url
    url = file_upload(file, document.project_id)

    document.url = url
    db.commit()

    file_delete(old_url)

    return doc_schemas.Document.model_validate(document)


def delete(
    document: doc_models.Document,
    user_id: UUID,
    db: Session,
) -> None:
    project = get_proj_by_id(document.project_id, db)
    if project.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden access"
        )

    file_delete(document.url)
    db.delete(document)
    db.commit()


def file_upload(file: UploadFile, proj_id: UUID) -> str:
    filename = f"{proj_id}_{file.filename}"
    path = (
        pathlib.Path(__file__).parent.parent.parent / "bucket" / "documents" / filename
    )
    with open(path, "wb+") as f:
        f.write(file.file.read())

    return str(path)


def file_delete(url: str) -> None:
    os.remove(url)
