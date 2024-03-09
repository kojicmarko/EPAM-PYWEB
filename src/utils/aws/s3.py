from typing import Any
from uuid import UUID

import boto3
from fastapi import UploadFile

from src.config import settings


class S3Client:
    def __init__(self) -> None:
        self.client = boto3.client("s3")

    def upload(self, file: UploadFile, proj_id: UUID, folder: str) -> str:
        self.client.upload_fileobj(
            file.file, settings.AWS_BUCKET_NAME, f"{folder}/{proj_id}_{file.filename}"
        )
        url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{folder}/{proj_id}_{file.filename}"
        return url

    def download(self, filename: str, folder: str) -> Any:
        res = self.client.get_object(
            Bucket=settings.AWS_BUCKET_NAME, Key=f"{folder}/{filename}"
        )
        return res

    def delete(self, filename: str, folder: str) -> None:
        self.client.delete_object(
            Bucket=settings.AWS_BUCKET_NAME, Key=f"{folder}/{filename}"
        )
