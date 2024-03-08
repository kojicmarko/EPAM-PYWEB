from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.files.dependencies import valid_file
from src.logos import models as logo_models
from src.logos import schemas as logo_schemas
from src.logos import service as logo_service
from src.logos.dependencies import get_logo_by_id
from src.projects import models as proj_models
from src.projects.dependencies import get_proj_by_id
from src.users import schemas as user_schemas
from src.users.dependencies import get_curr_user, is_participant
from src.utils.logger.main import logger

router = APIRouter()


@router.post("/projects/{proj_id}/logo", status_code=status.HTTP_201_CREATED)
def upload_logo(
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    logo: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> logo_schemas.Logo:
    log_msg = "User: %s, Uploaded: %s to Project: %s"
    logger.warning(log_msg, user.username, logo, project.name)
    return logo_service.create(logo, project, user, db)


@router.get(
    "/projects/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def download_logo(
    proj_id: UUID,
    proj_logo: Annotated[logo_models.Logo, Depends(get_logo_by_id)],
) -> StreamingResponse:
    res = logo_service.read(proj_logo, proj_id)
    return StreamingResponse(res["Body"])


@router.put(
    "/projects/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def update_logo(
    proj_id: UUID,
    logo: Annotated[logo_models.Logo, Depends(get_logo_by_id)],
    file: Annotated[UploadFile, Depends(valid_file)],
    db: Annotated[Session, Depends(get_db)],
) -> logo_schemas.Logo:
    log_msg = "Updated Logo: %s to Logo: %s"
    logger.warning(log_msg, logo, file)
    return logo_service.update(logo, proj_id, file, db)


@router.delete(
    "/projects/{proj_id}/logo",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_logo(
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    logo: Annotated[logo_models.Logo, Depends(get_logo_by_id)],
    curr_user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    logo_service.delete(logo, curr_user.id, project, db)
