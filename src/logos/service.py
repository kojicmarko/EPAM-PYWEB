from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.files import service as file_service
from src.logos import models as logo_models
from src.logos import schemas as logo_schemas
from src.projects import models as proj_models
from src.users import schemas as user_schemas


def create(
    name: str | None,
    url: str,
    project: proj_models.Project,
    user: user_schemas.User,
    db: Session,
) -> logo_schemas.Logo:
    logo = logo_models.Logo(name=name, url=url, owner_id=user.id)
    db.add(logo)
    db.commit()
    project.logo_id = logo.id
    db.commit()
    return logo_schemas.Logo.model_validate(logo)


def update(
    logo: logo_models.Logo, proj_id: UUID, file: UploadFile, db: Session
) -> logo_schemas.Logo:
    if file.filename is not None:
        logo.name = file.filename

    old_url = logo.url
    url = file_service.upload(file, proj_id)

    logo.url = url
    db.commit()

    file_service.delete(old_url)

    return logo_schemas.Logo.model_validate(logo)


def delete(
    logo: logo_models.Logo,
    project: proj_models.Project,
    db: Session,
) -> None:
    file_service.delete(logo.url)
    db.delete(logo)
    db.commit()
