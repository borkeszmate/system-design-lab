"""
Shared Event Schemas for Microservices Communication

Events are the contracts between services. They enable loose coupling
by allowing services to communicate without direct dependencies.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class OrderItem(BaseModel):
    """Item in an order"""
    product_id: int
    quantity: int
    price: Decimal


class OrderCreatedEvent(BaseModel):
    """
    Published by: Order Service
    Consumed by: Payment Service

    Triggered when a new order is successfully created.
    Payment service listens for this to process payment asynchronously.
    """
    event_type: str = "order.created"
    event_id: str
    timestamp: datetime

    # Order data
    order_id: int
    user_id: int
    user_email: str
    total_amount: Decimal
    items: List[OrderItem]

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class PaymentProcessedEvent(BaseModel):
    """
    Published by: Payment Service
    Consumed by: Email Service, Order Service

    Triggered when payment is successfully processed.
    Email service listens for this to send confirmation email.
    """
    event_type: str = "payment.processed"
    event_id: str
    timestamp: datetime

    # Payment data
    payment_id: int
    order_id: int
    user_id: int
    user_email: str
    amount: Decimal
    status: str  # 'completed', 'failed'
    transaction_id: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class PaymentFailedEvent(BaseModel):
    """
    Published by: Payment Service
    Consumed by: Order Service

    Triggered when payment fails. Order service can handle this
    by marking the order as failed and notifying the user.
    """
    event_type: str = "payment.failed"
    event_id: str
    timestamp: datetime

    # Failure data
    order_id: int
    user_id: int
    user_email: str
    amount: Decimal
    error_message: str

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class EmailSentEvent(BaseModel):
    """
    Published by: Email Service
    Consumed by: (optional) Notification Service, Analytics

    Triggered when email is successfully sent.
    Useful for tracking and analytics.
    """
    event_type: str = "email.sent"
    event_id: str
    timestamp: datetime

    # Email data
    recipient: str
    subject: str
    template: str
    order_id: Optional[int] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Event routing keys for RabbitMQ
class EventRoutingKeys:
    """
    Routing keys for RabbitMQ exchanges.
    Follows pattern: <service>.<entity>.<action>
    """
    ORDER_CREATED = "order.order.created"
    PAYMENT_PROCESSED = "payment.payment.processed"
    PAYMENT_FAILED = "payment.payment.failed"
    EMAIL_SENT = "email.email.sent"


# Queue names
class QueueNames:
    """Queue names for each service"""
    PAYMENT_QUEUE = "payment_service_queue"
    EMAIL_QUEUE = "email_service_queue"
    ORDER_UPDATES_QUEUE = "order_updates_queue"
