"""
RabbitMQ Event Publisher for Order Service

This module handles publishing events to RabbitMQ. Events are the primary
way microservices communicate asynchronously.
"""
import pika
import json
import logging
from datetime import datetime
from typing import Dict, Any
from .config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes events to RabbitMQ exchange.

    Uses topic exchange for flexible routing:
    - Payment Service listens to: order.order.created
    - Email Service listens to: payment.payment.processed
    """

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = "ecommerce_events"

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(settings.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare topic exchange (idempotent - safe to call multiple times)
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )

            logger.info("✅ Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise

    def publish_event(self, routing_key: str, event_data: Dict[str, Any]):
        """
        Publish an event to the exchange.

        Args:
            routing_key: Routing key (e.g., "order.order.created")
            event_data: Event payload as dict
        """
        if not self.channel:
            self.connect()

        try:
            message = json.dumps(event_data, default=str)

            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json',
                    timestamp=int(datetime.now().timestamp())
                )
            )

            logger.info(f"📤 Published event: {routing_key}")
            logger.debug(f"Event data: {message}")

        except Exception as e:
            logger.error(f"❌ Failed to publish event: {e}")
            raise

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("🔌 Closed RabbitMQ connection")


# Singleton instance
event_publisher = EventPublisher()
