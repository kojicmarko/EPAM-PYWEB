from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.files import service as file_service
from src.files.dependencies import valid_file
from src.logos import service as logo_service
from src.logos.dependencies import get_logo_by_id
from src.projects import models as proj_models
from src.projects.dependencies import get_proj_by_id
from src.users import schemas as user_schemas
from src.users.dependencies import is_participant

router = APIRouter()


@router.post("/projects/{proj_id}/logo", status_code=status.HTTP_201_CREATED)
def upload(
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    logo: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Logo:
    url = file_service.upload(logo, project.id)
    return logo_service.create(logo.filename, url, project, user, db)


@router.get(
    "/projects/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def download(
    proj_id: UUID,
    proj_logo: Annotated[doc_models.Logo, Depends(get_logo_by_id)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    logo = doc_schemas.Logo.model_validate(proj_logo)
    return FileResponse(logo.url, filename=logo.name)


@router.put(
    "/projects/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def update(
    proj_id: UUID,
    proj_logo: Annotated[doc_models.Logo, Depends(get_logo_by_id)],
    file: Annotated[UploadFile, Depends(valid_file)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Logo:
    return logo_service.update(proj_logo, proj_id, file, db)


@router.delete(
    "/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    proj_id: UUID,
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    proj_logo: Annotated[doc_models.Logo, Depends(get_logo_by_id)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    logo_service.delete(proj_logo, project, db)
