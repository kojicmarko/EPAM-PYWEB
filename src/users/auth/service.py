from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.config import settings
from src.users import models
from src.users import schemas as user_schemas
from src.users.auth import schemas as auth_schemas
from src.utils.auth import authenticate_user, create_token, pwd_context


def create(user: user_schemas.UserCreate, db: Session) -> user_schemas.User:
    hashed_password = pwd_context.hash(user.password)
    user_orm = models.User(username=user.username, password_hash=hashed_password)
    db.add(user_orm)
    db.commit()
    return user_schemas.User.model_validate(user_orm)


def login(
    form_data: OAuth2PasswordRequestForm, db: Session
) -> auth_schemas.Token | None:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return None
    token_expires = timedelta(minutes=float(settings.TOKEN_EXPIRE_TIME))
    token = create_token(
        data={"username": user.username, "id": str(user.id)},
        expires_delta=token_expires,
    )
    return auth_schemas.Token(token=token, type="bearer")
