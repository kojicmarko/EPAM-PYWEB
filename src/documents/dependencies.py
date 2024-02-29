from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.models import ProjectUser
from src.projects.dependencies import get_user
from src.projects.models import Project as ProjectModel
from src.users.schemas import User


def valid_filename(file: UploadFile) -> UploadFile:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file."
        )
    return file


def valid_file(file: Annotated[UploadFile, Depends(valid_filename)]) -> UploadFile:
    if file.content_type not in settings.valid_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type.",
        )
    return file


def is_participant(
    proj_id: UUID,
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    project_user = (
        db.query(ProjectUser)
        .filter(ProjectUser.user_id == user.id, ProjectUser.project_id == proj_id)
        .first()
    )

    project = db.query(ProjectModel).filter(ProjectModel.id == proj_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if not project_user and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized user.")

    return user
