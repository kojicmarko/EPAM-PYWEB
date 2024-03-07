from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from src.config import settings
from src.database import get_db
from src.models import ProjectUser
from src.users import models as user_models
from src.users import schemas
from src.utils.auth import MyOAuth2PasswordBearer
from src.utils.logger.main import logger

oauth2_scheme = MyOAuth2PasswordBearer(tokenUrl="login")


def get_user_by_username(
    username: str, db: Annotated[Session, Depends(get_db)]
) -> user_models.User:
    user = (
        db.query(user_models.User).filter(user_models.User.username == username).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def get_curr_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> schemas.User:
    logger.debug("HERE:")
    logger.debug(f"{token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err
    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    logger.debug(f"{schemas.User.model_validate(user)}")
    return schemas.User.model_validate(user)


def is_participant(
    proj_id: UUID,
    user: Annotated[schemas.User, Depends(get_curr_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.User:
    project_user = db.query(
        exists().where(
            ProjectUser.user_id == user.id, ProjectUser.project_id == proj_id
        )
    ).scalar()

    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden access"
        )

    return user
