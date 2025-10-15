"""
Application configuration settings.

Uses pydantic-settings for environment variable management.
"""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB/DocumentDB Configuration
    MONGODB_URL: str = "mongodb://admin:password123@documentdb:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256"
    MONGODB_DB_NAME: str = "ecommerce"
    
    # Application Settings
    APP_NAME: str = "FastAPI E-Commerce"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    RELOAD: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


# Create global settings instance
settings = Settings()
