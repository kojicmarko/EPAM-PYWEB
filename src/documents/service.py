import pathlib
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.documents import models
from src.documents.schemas import Document
from src.users.schemas import User


def create(
    name: str | None, url: str, proj_id: UUID, user: User, db: Session
) -> Document:
    document = models.Document(name=name, url=url, owner_id=user.id, project_id=proj_id)
    db.add(document)
    db.commit()
    return Document.model_validate(document)


async def file_upload(file: UploadFile, proj_id: UUID) -> str:
    filename = f"{proj_id}_{file.filename}"
    path = (
        pathlib.Path(__file__).parent.parent.parent / "bucket" / "documents" / filename
    )
    with open(path, "wb+") as f:
        contents = await file.read()
        f.write(contents)

    return str(path)
