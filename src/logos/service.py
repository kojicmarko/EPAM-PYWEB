from typing import Any
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.logos import models as logo_models
from src.logos import schemas as logo_schemas
from src.projects import models as proj_models
from src.users import schemas as user_schemas
from src.utils.aws.s3 import S3Client
from src.utils.logger.main import logger

s3 = S3Client()


def read(logo: logo_models.Logo, proj_id: UUID) -> Any:
    logo_schema = logo_schemas.Logo.model_validate(logo)
    res = s3.download(f"{proj_id}_{logo_schema.name}", "logos")
    return res


def create(
    logo_file: UploadFile,
    project: proj_models.Project,
    user: user_schemas.User,
    db: Session,
) -> logo_schemas.Logo:
    url = s3.upload(logo_file, project.id, "logos")

    logo = logo_models.Logo(name=str(logo_file.filename), url=url, owner_id=user.id)

    db.add(logo)
    db.commit()

    project.logo_id = logo.id
    db.commit()

    return logo_schemas.Logo.model_validate(logo)


def update(
    logo: logo_models.Logo, proj_id: UUID, file: UploadFile, db: Session
) -> logo_schemas.Logo:
    s3.delete(f"{proj_id}_{logo.name}", "logos")

    logo.name = str(file.filename)
    logo.url = s3.upload(file, proj_id, "logos")
    db.commit()

    return logo_schemas.Logo.model_validate(logo)


def delete(
    logo: logo_models.Logo,
    curr_user_id: UUID,
    project: proj_models.Project,
    db: Session,
) -> None:
    if project.owner_id != curr_user_id:
        log_msg = "Current User: %s - IS NOT OWNER - Owner: %s"
        logger.error(log_msg, curr_user_id, project.owner_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Project owner can delete the Logo",
        )

    s3.delete(f"{project.id}_{logo.name}", "logos")
    db.delete(logo)
    db.commit()
