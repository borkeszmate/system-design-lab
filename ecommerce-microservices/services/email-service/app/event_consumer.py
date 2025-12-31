"""
RabbitMQ Event Consumer for Email Service

This consumer listens for PaymentProcessed events and sends confirmation emails.
"""
import pika
import json
import logging
from .config import settings
from .email_sender import send_order_confirmation_email

logger = logging.getLogger(__name__)


class EmailEventConsumer:
    """
    Consumes PaymentProcessed events and sends confirmation emails.

    This is the final step in the async checkout flow:
    1. User clicks checkout
    2. Order Service creates order (~300ms) - user gets response
    3. Payment Service processes payment (~1s) - in background
    4. Email Service sends email (~2s) - in background
    """

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = "ecommerce_events"
        self.queue_name = "email_service_queue"
        self.routing_key = "payment.payment.processed"

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(settings.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare exchange (idempotent)
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )

            # Declare queue (idempotent)
            self.channel.queue_declare(queue=self.queue_name, durable=True)

            # Bind queue to exchange with routing key
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.routing_key
            )

            logger.info(f"✅ Connected to RabbitMQ")
            logger.info(f"📥 Listening for events: {self.routing_key}")

        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise

    def send_confirmation_email(self, payment_data: dict):
        """Send order confirmation email"""
        try:
            send_order_confirmation_email(
                user_email=payment_data['user_email'],
                order_id=payment_data['order_id'],
                amount=payment_data['amount'],
                transaction_id=payment_data.get('transaction_id', 'N/A')
            )
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            # In production: implement retry logic

    def callback(self, ch, method, properties, body):
        """Callback function for consuming messages"""
        try:
            # Parse event data
            event_data = json.loads(body)
            logger.info(f"📥 Received event: {event_data['event_type']}")

            # Send email
            if event_data.get('status') == 'completed':
                self.send_confirmation_email(event_data)
            else:
                logger.warning(f"⚠️  Payment not completed, skipping email")

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        """Start consuming messages from the queue"""
        try:
            self.connect()
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback
            )

            logger.info("🎧 Email Service is listening for events...")
            logger.info("Press CTRL+C to exit")
            self.channel.start_consuming()

        except KeyboardInterrupt:
            logger.info("🛑 Stopping Email Service...")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}")
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("🔌 Disconnected from RabbitMQ")
