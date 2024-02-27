from datetime import datetime, timedelta
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config import algorithm, secret_key
from src.database import get_db
from src.users import models
from src.users.schemas import User, UserAuth

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(
    db: Session, username: str, password: str
) -> User | Literal[False]:
    user_orm = db.query(models.User).filter(models.User.username == username).first()

    if not user_orm:
        return False
    if not verify_password(password, user_orm.password_hash):
        return False
    user = UserAuth.model_validate(user_orm)

    return user


def create_token(data: dict[str, str | datetime], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


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
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return User.model_validate(user)
