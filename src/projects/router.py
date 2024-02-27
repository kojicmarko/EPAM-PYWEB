from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.auth.utils import get_user
from src.database import get_db
from src.projects import service as project_service
from src.projects.schemas import Project, ProjectCreate, ProjectUpdate
from src.users.schemas import User
from src.utils.logger.main import logger

router = APIRouter(prefix="/projects")


@router.get("/", status_code=status.HTTP_200_OK)
def read_projects(
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Project]:
    return project_service.read_all(user.id, db)


@router.get("/{proj_id}/info", status_code=status.HTTP_200_OK)
def read_project(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Project:
    project = project_service.read(proj_id, user.id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Project:
    logger.debug(f"User {user.username}, Created Project {project.model_dump()}")
    new_project = project_service.create(project, user.id, db)
    return new_project


@router.put("/{proj_id}/info", status_code=status.HTTP_200_OK)
def update_project(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    project: ProjectUpdate,
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Project:
    updated_project = project_service.update(proj_id, project, user.id, db)
    if not updated_project:
        raise HTTPException(
            status_code=404, detail=f"Project with {proj_id} does not exist."
        )
    return updated_project


@router.delete("/{proj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    deleted_project = project_service.delete(proj_id, user.id, db)
    if not deleted_project:
        raise HTTPException(
            status_code=404, detail=f"Project with {proj_id} does not exist."
        )


@router.post("/{proj_id}/invite", status_code=status.HTTP_201_CREATED)
def invite(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    user: Annotated[str, Query(...)],
    db: Annotated[Session, Depends(get_db)],
    owner: Annotated[User, Depends(get_user)],
) -> None:
    is_invited = project_service.invite(proj_id, user, owner.id, db)
    if not is_invited:
        raise HTTPException(
            status_code=403, detail="Cannot invite user to the project."
        )
