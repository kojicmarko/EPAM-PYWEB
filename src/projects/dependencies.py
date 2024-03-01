from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.projects import models


def get_proj_by_id(
    proj_id: UUID, db: Annotated[Session, Depends(get_db)]
) -> models.Project:
    project = db.query(models.Project).filter(models.Project.id == proj_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project
