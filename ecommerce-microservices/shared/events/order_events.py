"""
Shared event schemas for RabbitMQ messaging

This ensures consistency across services that publish/consume events.
"""
from pydantic import BaseModel
from decimal import Decimal
from typing import List
from datetime import datetime


class OrderItem(BaseModel):
    """Order item schema"""
    product_id: int
    quantity: int
    price: Decimal


class OrderCreatedEvent(BaseModel):
    """Event published when order is created"""
    event_type: str = "order.created"
    order_id: int
    user_id: int
    user_email: str
    items: List[OrderItem]
    total_amount: Decimal
    timestamp: datetime


class PaymentProcessedEvent(BaseModel):
    """Event published when payment is processed"""
    event_type: str = "payment.processed"
    order_id: int
    payment_id: int
    status: str  # "completed" or "failed"
    timestamp: datetime
