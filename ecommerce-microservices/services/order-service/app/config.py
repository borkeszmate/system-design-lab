"""Configuration for Order Service"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://order_user:order123@order-db:5432/order_db"

    # RabbitMQ
    rabbitmq_url: str = "amqp://ecommerce:ecommerce123@rabbitmq:5672/"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
