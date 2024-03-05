from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.projects import models as proj_models
from src.projects import schemas as proj_schemas
from src.projects import service as proj_service
from src.projects.dependencies import get_proj_by_id
from src.users import schemas as user_schemas
from src.users.dependencies import get_curr_user, is_participant
from src.utils.logger.main import logger

router = APIRouter(prefix="/projects")


@router.get("/", status_code=status.HTTP_200_OK)
def read_projects(
    curr_user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[proj_schemas.Project]:
    return proj_service.read_all(curr_user.id, db)


@router.get(
    "/{proj_id}/info",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def read_project(
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
) -> proj_schemas.Project:
    return proj_service.read(project)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    project: proj_schemas.ProjectCreate,
    curr_user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> proj_schemas.Project:
    logger.debug(f"User {curr_user.username}, Created Project {project.model_dump()}")
    return proj_service.create(project, curr_user.id, db)


@router.put(
    "/{proj_id}/info",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def update_project(
    proj_update: proj_schemas.ProjectUpdate,
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    db: Annotated[Session, Depends(get_db)],
) -> proj_schemas.Project:
    return proj_service.update(project, proj_update, db)


@router.delete("/{proj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    user: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    return proj_service.delete(project, user.id, db)


@router.post("/{proj_id}/invite", status_code=status.HTTP_201_CREATED)
def invite_to_project(
    project: Annotated[proj_models.Project, Depends(get_proj_by_id)],
    user: Annotated[str, Query(...)],
    owner: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    return proj_service.invite(project, user, owner.id, db)
