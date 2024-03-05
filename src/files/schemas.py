from pydantic import BaseModel, Field


class FileBase(BaseModel):
    name: str = Field(max_length=40)
