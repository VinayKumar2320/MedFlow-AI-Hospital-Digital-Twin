"""Core configuration management using Pydantic Settings."""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "MedFlow — Hospital Operations Digital Twin"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./medflow.db",
        description="Database connection URL. SQLite default for local zero-config; supports PostgreSQL."
    )

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Simulation & Operational Defaults
    DEFAULT_RANDOM_SEED: int = 42
    MAX_SIMULATION_HOURS: int = 168  # 1 week max
    DEFAULT_SIMULATION_HOURS: int = 48
    MAX_MONTE_CARLO_REPLICATIONS: int = 30
    DEFAULT_MONTE_CARLO_REPLICATIONS: int = 5

    # Optimizer Defaults
    OPTIMIZER_TIME_LIMIT_SECONDS: int = 30
    HOURLY_COST_PHYSICIAN: float = 180.0
    HOURLY_COST_NURSE: float = 65.0
    HOURLY_COST_TECH: float = 40.0
    HOURLY_COST_BED: float = 25.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
