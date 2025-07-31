from minio import Minio
from minio.error import S3Error
import os
import logging

MINIO_HOST = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT = os.getenv("MINIO_PORT", "9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "my-bucket")
MINIO_SECURE = os.getenv("MINIO_SECURE", False)

minio_client = Minio(
    endpoint=f"{MINIO_HOST}:{MINIO_PORT}",
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=MINIO_SECURE  # True nếu MinIO bật HTTPS
)


def setup_minio_bucket():
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            logging.info(f"✅ Created bucket: {MINIO_BUCKET}")
        else:
            logging.info(f"✅ Bucket already exists: {MINIO_BUCKET}")
    except S3Error as e:
        logging.error(f"❌ MinIO setup error: {e}")
        raise