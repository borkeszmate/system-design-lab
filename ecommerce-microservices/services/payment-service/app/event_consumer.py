"""
RabbitMQ Event Consumer for Payment Service

This consumer listens for OrderCreated events and processes payments asynchronously.
"""
import pika
import json
import time
import uuid
import logging
from datetime import datetime
from decimal import Decimal

from .database import SessionLocal
from .models import Payment
from .config import settings

logger = logging.getLogger(__name__)


class PaymentEventConsumer:
    """
    Consumes OrderCreated events and processes payments.

    This is the key to async processing:
    - Listens to RabbitMQ queue
    - Processes payments in the background
    - User doesn't wait for this!
    """

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = "ecommerce_events"
        self.queue_name = "payment_service_queue"
        self.routing_key = "order.order.created"

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

    def process_payment(self, order_data: dict):
        """
        Process payment for an order.

        This simulates the 1-second payment gateway call from the monolith,
        but now it happens ASYNCHRONOUSLY - the user doesn't wait!
        """
        logger.info("=" * 80)
        logger.info(f"💳 [Payment Service] Processing payment for order #{order_data['order_id']}")
        logger.info(f"💰 Amount: ${order_data['total_amount']}")
        logger.info("⚡ This happens in BACKGROUND - user already got their response!")
        logger.info("=" * 80)

        # Create payment record
        db = SessionLocal()
        try:
            payment = Payment(
                order_id=order_data['order_id'],
                user_id=order_data['user_id'],
                amount=Decimal(order_data['total_amount']),
                status='pending'
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            logger.info("[Step 1/3] Payment record created in database")

            # Simulate payment gateway call (1 second delay, same as monolith)
            logger.info("[Step 2/3] Calling payment gateway...")
            logger.info("💀 BLOCKING OPERATION - but user doesn't wait for this!")
            time.sleep(1)  # Simulate payment gateway delay

            # Update payment status
            payment.status = 'completed'
            payment.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            db.commit()

            logger.info(f"✅ Payment completed! Transaction: {payment.transaction_id}")

            # Publish PaymentProcessed event
            logger.info("[Step 3/3] Publishing PaymentProcessed event...")
            self.publish_payment_event(payment, order_data)

            logger.info("=" * 80)
            logger.info("🎉 Payment processed successfully!")
            logger.info("📤 Email Service will now send confirmation email")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ Payment failed: {e}")
            if payment:
                payment.status = 'failed'
                db.commit()
            # In production: publish PaymentFailed event, implement retry logic
        finally:
            db.close()

    def publish_payment_event(self, payment: Payment, order_data: dict):
        """Publish PaymentProcessed event for Email Service"""
        event_data = {
            "event_type": "payment.processed",
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "user_id": payment.user_id,
            "user_email": order_data['user_email'],
            "amount": str(payment.amount),
            "status": payment.status,
            "transaction_id": payment.transaction_id
        }

        try:
            message = json.dumps(event_data, default=str)
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="payment.payment.processed",
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            logger.info("📤 PaymentProcessed event published")
        except Exception as e:
            logger.error(f"❌ Failed to publish event: {e}")

    def callback(self, ch, method, properties, body):
        """
        Callback function for consuming messages.
        """
        try:
            # Parse event data
            event_data = json.loads(body)
            logger.info(f"📥 Received event: {event_data['event_type']}")

            # Process payment
            self.process_payment(event_data)

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            # In production: send to dead-letter queue, implement retry logic
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        """Start consuming messages from the queue"""
        try:
            self.connect()
            self.channel.basic_qos(prefetch_count=1)  # Process one message at a time
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback
            )

            logger.info("🎧 Payment Service is listening for events...")
            logger.info("Press CTRL+C to exit")
            self.channel.start_consuming()

        except KeyboardInterrupt:
            logger.info("🛑 Stopping Payment Service...")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}")
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("🔌 Disconnected from RabbitMQ")
