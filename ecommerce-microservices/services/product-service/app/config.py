"""Configuration for Product Service"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "Product Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://product_user:product123@product-db:5432/product_db"
    )

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8004

    class Config:
        case_sensitive = True


settings = Settings()
