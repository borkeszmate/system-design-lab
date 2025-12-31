from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "E-Commerce Monolith"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Email (simulated - intentionally synchronous and slow)
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025  # Using MailHog for local testing
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@ecommerce.com"
    EMAIL_DELAY_SECONDS: int = 2  # Intentional delay to demonstrate blocking

    # Payment (simulated)
    PAYMENT_API_URL: str = "http://fake-payment-api.com"
    PAYMENT_DELAY_SECONDS: int = 1  # Intentional delay

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
