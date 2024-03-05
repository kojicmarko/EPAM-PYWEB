from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.files import schemas as file_schemas


class DocumentCreate(file_schemas.FileBase):
    pass


class Document(file_schemas.FileBase):
    model_config = ConfigDict(from_attributes=True)

    url: str
    id: UUID
    owner_id: UUID
    project_id: UUID


class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(max_length=40)


class PaginatedDocuments(BaseModel):
    documents: Optional[list[Document]]
    count: Optional[int]
    next: Optional[int]
    prev: Optional[int]
