from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile, status

from src.config import settings


def valid_filename(file: UploadFile) -> UploadFile:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file"
        )
    return file


def valid_file(file: Annotated[UploadFile, Depends(valid_filename)]) -> UploadFile:
    if file.content_type not in settings.valid_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type",
        )
    return file
