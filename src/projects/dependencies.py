from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.projects.models import Project as ProjectModel
from src.users.models import User as UserModel
from src.users.schemas import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise credentials_exception
    return User.model_validate(user)


def get_proj_by_id(
    proj_id: UUID, db: Annotated[Session, Depends(get_db)]
) -> ProjectModel:
    project = db.query(ProjectModel).filter(ProjectModel.id == proj_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
