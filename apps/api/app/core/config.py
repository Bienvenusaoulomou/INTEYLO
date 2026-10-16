"""Configuration chargée depuis l'environnement (préfixe INTEYLO_).

Chaque variable peut aussi être fournie par fichier : INTEYLO_DATABASE_URL_FILE=/run/secrets/x
lit la valeur dans le fichier (secrets Docker).
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "staging", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INTEYLO_", extra="ignore")

    environment: Environment = "development"
    database_url: str
    session_ttl_hours: int = 168
    cookie_secure: bool = True
    cors_origins: list[str] = []
    invitation_ttl_hours: int = 72
    login_max_attempts: int = 10
    login_window_seconds: int = 900
    public_web_url: str = "http://localhost:3000"
    log_level: str = "INFO"


def _load_file_variables() -> None:
    for key, value in list(os.environ.items()):
        if key.startswith("INTEYLO_") and key.endswith("_FILE"):
            target = key.removesuffix("_FILE")
            if target not in os.environ:
                os.environ[target] = Path(value).read_text(encoding="utf-8").strip()


@lru_cache
def get_settings() -> Settings:
    _load_file_variables()
    return Settings()
