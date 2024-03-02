from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.documents import models as doc_models
from src.documents import schemas as doc_schemas
from src.documents import service as doc_service
from src.documents.dependencies import valid_file
from src.logos import service as logo_service
from src.logos.dependencies import get_logo_by_id
from src.projects import models
from src.projects import schemas as proj_schemas
from src.projects import service as project_service
from src.projects.dependencies import get_proj_by_id
from src.users import schemas as user_schemas
from src.users.dependencies import get_curr_user, is_participant
from src.utils.logger.main import logger

router = APIRouter(prefix="/projects")


@router.get("/", status_code=status.HTTP_200_OK)
def read_projects(
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[proj_schemas.Project]:
    return project_service.read_all(user.id, db)


@router.get("/{proj_id}/info", status_code=status.HTTP_200_OK)
def read_project(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> proj_schemas.Project:
    project = project_service.read(proj_id, user.id, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return project


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    project: proj_schemas.ProjectCreate,
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> proj_schemas.Project:
    logger.debug(f"User {user.username}, Created Project {project.model_dump()}")
    return project_service.create(project, user.id, db)


@router.put("/{proj_id}/info", status_code=status.HTTP_200_OK)
def update_project(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    project: proj_schemas.ProjectUpdate,
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> proj_schemas.Project:
    updated_project = project_service.update(proj_id, project, user.id, db)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return updated_project


@router.delete("/{proj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    user: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    deleted_project = project_service.delete(proj_id, user.id, db)
    if not deleted_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


@router.post("/{proj_id}/invite", status_code=status.HTTP_201_CREATED)
def invite(
    proj_id: Annotated[UUID, Path(title="Project ID")],
    user: Annotated[str, Query(...)],
    owner: Annotated[user_schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    is_invited = project_service.invite(proj_id, user, owner.id, db)
    if not is_invited:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden access",
        )


@router.post("/{proj_id}/documents", status_code=status.HTTP_201_CREATED)
def upload_document(
    proj_id: UUID,
    document: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Document:
    url = doc_service.file_upload(document, proj_id)
    return doc_service.create(document.filename, url, proj_id, user, db)


@router.get(
    "/{proj_id}/documents",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def read_documents(
    project: Annotated[models.Project, Depends(get_proj_by_id)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(5, ge=1, le=10, title="Limit"),
    offset: int = Query(0, ge=0, title="Offset"),
) -> doc_schemas.PaginatedDocuments:
    if not project.documents:
        return doc_schemas.PaginatedDocuments(
            documents=[], count=0, next=None, prev=None
        )
    return doc_service.read_all(project.id, limit, offset, db)


@router.post("/{proj_id}/logo", status_code=status.HTTP_201_CREATED)
def upload_logo(
    project: Annotated[models.Project, Depends(get_proj_by_id)],
    logo: Annotated[UploadFile, Depends(valid_file)],
    user: Annotated[user_schemas.User, Depends(is_participant)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Logo:
    url = doc_service.file_upload(logo, project.id)
    return logo_service.create(logo.filename, url, project, user, db)


@router.get(
    "/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def download_logo(
    proj_id: UUID,
    proj_logo: Annotated[doc_models.Logo, Depends(get_logo_by_id)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    logger.debug(proj_logo)
    logo = doc_schemas.Logo.model_validate(proj_logo)
    return FileResponse(logo.url, filename=logo.name)


@router.put(
    "/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_200_OK,
)
def update(
    proj_id: UUID,
    proj_logo: Annotated[doc_models.Logo, Depends(get_logo_by_id)],
    file: Annotated[UploadFile, Depends(valid_file)],
    db: Annotated[Session, Depends(get_db)],
) -> doc_schemas.Logo:
    logger.debug(logo_service.update(proj_logo, proj_id, file, db))
    return logo_service.update(proj_logo, proj_id, file, db)


@router.delete(
    "/{proj_id}/logo",
    dependencies=[Depends(is_participant)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    proj_id: UUID,
    project: Annotated[models.Project, Depends(get_proj_by_id)],
    proj_logo: Annotated[doc_models.Logo, Depends(get_logo_by_id)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    logo_service.delete(proj_logo, project, db)
