from __future__ import annotations
import os
from dataclasses import dataclass

def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)

@dataclass(frozen=True)
class Settings:
    app_name: str = _env("APP_NAME", "PharmaLens AI")
    app_env: str = _env("APP_ENV", "development")
    api_host: str = _env("API_HOST", "0.0.0.0")
    api_port: int = int(_env("API_PORT", "8000"))
    log_level: str = _env("LOG_LEVEL", "INFO")
    data_path: str = _env("DATA_PATH", "data/processed/cleaned_pharma_data.parquet")
    model_provider: str = _env("MODEL_PROVIDER", "")
    model_name: str = _env("MODEL_NAME", "")

settings = Settings()
