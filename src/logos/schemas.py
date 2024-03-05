from uuid import UUID

from pydantic import ConfigDict

from src.files import schemas as file_schemas


class Logo(file_schemas.FileBase):
    model_config = ConfigDict(from_attributes=True)

    url: str
    id: UUID
    owner_id: UUID
