"""Configuration for Payment Service"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://payment_user:payment123@payment-db:5432/payment_db"

    # RabbitMQ
    rabbitmq_url: str = "amqp://ecommerce:ecommerce123@rabbitmq:5672/"

    class Config:
        env_file = ".env"


settings = Settings()
