import os

import boto3
from PIL import Image

client = boto3.client("s3")


def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    download_path = f"/tmp/{os.path.basename(key)}"
    client.download_file(bucket, key, download_path)

    with Image.open(download_path) as img:
        img.thumbnail((400, 400))

        img.save(download_path)

    client.upload_file(download_path, bucket, key)
