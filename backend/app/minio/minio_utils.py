# app/minio/minio_utils.py
from minio.error import S3Error
from app.minio.minio_config import minio_client, MINIO_BUCKET
import logging
from typing import Union
from pathlib import Path


def upload_file(file_path: Union[str, Path], object_name: str, content_type: str = "application/octet-stream"):
    """Upload a file to MinIO."""
    try:
        file_path = Path(file_path)
        minio_client.fput_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            file_path=str(file_path),
            content_type=content_type,
        )
        logging.info(f"✅ Uploaded file to MinIO: {object_name}")
    except S3Error as e:
        logging.error(f"❌ Error uploading file: {e}")
        raise


def download_file(object_name: str, file_path: Union[str, Path]):
    """Download a file from MinIO."""
    try:
        file_path = Path(file_path)
        minio_client.fget_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            file_path=str(file_path)
        )
        logging.info(f"✅ Downloaded file from MinIO: {object_name}")
    except S3Error as e:
        logging.error(f"❌ Error downloading file: {e}")
        raise


def delete_file(object_name: str):
    """Delete a file from MinIO."""
    try:
        minio_client.remove_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name
        )
        logging.info(f"🗑️ Deleted file from MinIO: {object_name}")
    except S3Error as e:
        logging.error(f"❌ Error deleting file: {e}")
        raise
