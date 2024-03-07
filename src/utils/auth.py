from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config import settings
from src.users import models, schemas


def get_authorization_scheme_param(
    authorization_header_value: Optional[str],
) -> tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


class MyOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("MyAuthorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = MyOAuth2PasswordBearer(tokenUrl="login")


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> schemas.User | None:
    user_orm = db.query(models.User).filter(models.User.username == username).first()

    if not user_orm:
        return None
    if not verify_password(password, user_orm.password_hash):
        return None
    user = schemas.UserAuth.model_validate(user_orm)

    return user


def create_token(data: dict[str, str | datetime], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
