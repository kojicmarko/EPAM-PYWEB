from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth.schemas import Token
from src.auth.utils import authenticate_user, create_token, pwd_context
from src.config import token_expire_time
from src.users import models
from src.users.schemas import User, UserCreate


def create(user: UserCreate, db: Session) -> User:
    hashed_password = pwd_context.hash(user.password)
    user_orm = models.User(username=user.username, password_hash=hashed_password)
    db.add(user_orm)
    db.commit()
    return User.model_validate(user_orm)


def login(form_data: OAuth2PasswordRequestForm, db: Session) -> Token | None:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return None
    token_expires = timedelta(minutes=float(token_expire_time))
    token = create_token(
        data={"username": user.username, "id": str(user.id)},
        expires_delta=token_expires,
    )
    return Token(token=token, type="bearer")
