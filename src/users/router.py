from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import get_db
from src.users import schemas as user_schemas
from src.users.auth import schemas as auth_schemas
from src.users.auth import service as auth_service
from src.utils.logger.main import logger

router = APIRouter()


@router.post("/auth", status_code=status.HTTP_201_CREATED)
def create_user(
    user: user_schemas.UserCreate, db: Annotated[Session, Depends(get_db)]
) -> user_schemas.User:
    logger.debug(f"Created User {user.model_dump()}")
    return auth_service.create(user, db)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> auth_schemas.Token:
    user = auth_service.login(form_data, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
