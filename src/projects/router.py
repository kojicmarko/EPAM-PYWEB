from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.projects import service as project_service
from src.projects.schemas import Project, ProjectCreate, ProjectUpdate
from src.utils.logger.main import logger

router = APIRouter(prefix="/projects")


@router.get("/", status_code=status.HTTP_200_OK)
def read_projects(db: Session = Depends(get_db)) -> list[Project]:
    return project_service.read_all(db)


@router.get("/{proj_id}/info", status_code=status.HTTP_200_OK)
def read_project(proj_id: str, db: Session = Depends(get_db)) -> Project:
    project = project_service.read(proj_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    logger.debug(f"Created Project {project.model_dump()}")
    new_project = project_service.create(project, db)
    return new_project


@router.put("/{proj_id}/info", status_code=status.HTTP_200_OK)
def update_project(
    proj_id: str, project: ProjectUpdate, db: Session = Depends(get_db)
) -> Project:
    updated_project = project_service.update(proj_id, project, db)
    if not updated_project:
        raise HTTPException(
            status_code=404, detail=f"Project with {proj_id} does not exist."
        )
    return updated_project


@router.delete("/{proj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(proj_id: str, db: Session = Depends(get_db)) -> None:
    deleted_project = project_service.delete(proj_id, db)
    if not deleted_project:
        raise HTTPException(
            status_code=404, detail=f"Project with {proj_id} does not exist."
        )
