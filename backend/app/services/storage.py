"""
Cloud Storage helper for uploaded survey images.
"""

import uuid
from google.cloud import storage
from app.config import get_settings


def upload_image(file_bytes: bytes, filename: str, content_type: str = "image/png") -> str:
    """
    Upload an image to Google Cloud Storage and return its public URL.
    """
    settings = get_settings()
    client = storage.Client()
    bucket = client.bucket(settings.gcs_bucket_name)

    unique_name = f"surveys/{uuid.uuid4()}-{filename}"
    blob = bucket.blob(unique_name)

    blob.upload_from_string(file_bytes, content_type=content_type)
    blob.make_public()

    return blob.public_url
