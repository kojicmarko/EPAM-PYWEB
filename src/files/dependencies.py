from fastapi import HTTPException, UploadFile, status

from src.config import settings
from src.utils.logger.main import logger


def valid_file(file: UploadFile) -> UploadFile:
    if not file.filename:
        logger.error(file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file"
        )
    if file.content_type not in settings.VALID_TYPES:
        logger.error(file.content_type)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type",
        )
    return file
