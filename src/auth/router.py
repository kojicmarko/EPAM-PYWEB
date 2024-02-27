from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth import service as auth_service
from src.auth.schemas import Token
from src.database import get_db
from src.users.schemas import User, UserCreate
from src.utils.logger.main import logger

router = APIRouter()


@router.post("/auth", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    logger.debug(f"Created User {user.model_dump()}")
    return auth_service.create(user, db)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = auth_service.login(form_data, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
