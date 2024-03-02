from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    name: str = Field(max_length=40)


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
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


class Logo(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    url: str
    id: UUID
    owner_id: UUID
