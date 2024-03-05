from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.files import schemas as file_schemas


class Document(file_schemas.FileBase):
    model_config = ConfigDict(from_attributes=True)

    url: str
    id: UUID
    owner_id: UUID
    project_id: UUID


class PaginatedDocuments(BaseModel):
    documents: Optional[list[Document]]
    count: Optional[int]
    next: Optional[int]
    prev: Optional[int]
