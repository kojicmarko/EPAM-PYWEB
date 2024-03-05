import os
import pathlib
from uuid import UUID

from fastapi import UploadFile


def upload(file: UploadFile, proj_id: UUID) -> str:
    filename = f"{proj_id}_{file.filename}"
    if file.content_type == "image/png" or file.content_type == "image/jpeg":
        path = (
            pathlib.Path(__file__).parent.parent.parent / "bucket" / "logos" / filename
        )
    else:
        path = (
            pathlib.Path(__file__).parent.parent.parent
            / "bucket"
            / "documents"
            / filename
        )

    with open(path, "wb+") as f:
        f.write(file.file.read())

    return str(path)


def delete(url: str) -> None:
    os.remove(url)
