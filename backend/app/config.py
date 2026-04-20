import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    google_cloud_project: str = "sra-backend-2026"
    google_application_credentials: str = "./service-account-key.json"
    gemini_api_key: str = ""
    cloud_storage_bucket: str = "sra-survey-images-2026"
    google_maps_api_key: str = ""
    firebase_project_id: str = "sra-backend-2026"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    credentials_path = Path(settings.google_application_credentials)
    if not credentials_path.is_absolute():
        credentials_path = BASE_DIR / credentials_path
    settings.google_application_credentials = str(credentials_path)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
    return settings