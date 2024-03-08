import os
import pathlib
from uuid import UUID

from fastapi import UploadFile


def upload(file: UploadFile, proj_id: UUID, folder: str) -> str:
    filename = f"{proj_id}_{file.filename}"

    path = pathlib.Path(__file__).parent.parent.parent / "bucket" / folder / filename

    with open(path, "wb+") as f:
        f.write(file.file.read())

    return str(path)


def delete(path: str) -> None:
    os.remove(path)
