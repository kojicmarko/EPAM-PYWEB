from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(max_length=30)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class UserAuth(User):
    password_hash: str
