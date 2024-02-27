from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(max_length=40)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(max_length=40)
    description: Optional[str] = None
