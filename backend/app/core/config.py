from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Drosophila Brain Explorer"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database (SQLite для dev, PostgreSQL для prod)
    DATABASE_URL: str = "sqlite+aiosqlite:///./dro_dev.db"

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Data paths
    DATA_DIR: str = "../data"
    PATH_CONNECTOME: str = "../data/connections.parquet"
    PATH_COMPLETENESS: str = "../data/completeness.csv"
    RESULTS_DIR: str = "../data/results"

    # Simulation defaults
    DEFAULT_T_RUN: float = 1000.0
    DEFAULT_N_RUN: int = 30
    DEFAULT_N_PROC: int = -1

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
