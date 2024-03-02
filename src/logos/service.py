from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.documents import service as doc_service
from src.projects import models as proj_models
from src.users import schemas as user_schemas


def create(
    name: str | None,
    url: str,
    project: proj_models.Project,
    user: user_schemas.User,
    db: Session,
) -> doc_schemas.Logo:
    logo = doc_models.Logo(name=name, url=url, owner_id=user.id)
    db.add(logo)
    db.commit()
    project.logo_id = logo.id
    db.commit()
    return doc_schemas.Logo.model_validate(logo)


def update(
    logo: doc_models.Logo, proj_id: UUID, file: UploadFile, db: Session
) -> doc_schemas.Logo:
    if file.filename is not None:
        logo.name = file.filename

    old_url = logo.url
    url = doc_service.file_upload(file, proj_id)

    logo.url = url
    db.commit()

    doc_service.file_delete(old_url)

    return doc_schemas.Logo.model_validate(logo)


def delete(
    logo: doc_models.Logo,
    project: proj_models.Project,
    db: Session,
) -> None:
    doc_service.file_delete(logo.url)
    db.delete(logo)
    db.commit()
