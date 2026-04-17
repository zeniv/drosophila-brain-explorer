from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Drosophila Brain Explorer"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://dro:dro_pass@postgres:5432/dro_db"

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]

    # Data paths (внутри контейнера)
    DATA_DIR: str = "/app/data"
    PATH_CONNECTOME: str = "/app/data/connections.parquet"
    PATH_COMPLETENESS: str = "/app/data/completeness.csv"
    RESULTS_DIR: str = "/app/data/results"

    # Simulation defaults
    DEFAULT_T_RUN: float = 1000.0    # ms
    DEFAULT_N_RUN: int = 30
    DEFAULT_N_PROC: int = -1         # -1 = all CPUs

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
