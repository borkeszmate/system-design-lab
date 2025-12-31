"""Configuration for Email Service"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # RabbitMQ
    rabbitmq_url: str = "amqp://ecommerce:ecommerce123@rabbitmq:5672/"

    # SMTP (MailHog)
    smtp_host: str = "mailhog"
    smtp_port: int = 1025

    class Config:
        env_file = ".env"


settings = Settings()
