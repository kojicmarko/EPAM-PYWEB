from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.logos import models as logo_models
from src.projects.dependencies import get_proj_by_id
from src.utils.logger.main import logger


def get_logo_by_id(
    proj_id: UUID, db: Annotated[Session, Depends(get_db)]
) -> logo_models.Logo:
    project = get_proj_by_id(proj_id, db)
    logo_id = project.logo_id
    logo = db.query(logo_models.Logo).filter(logo_models.Logo.id == logo_id).first()
    if not logo:
        logger.error(logo)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Logo not found"
        )
    return logo
