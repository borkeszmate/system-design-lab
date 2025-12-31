from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import List, Optional
from app.models.order import OrderStatus


# Order Item Schemas
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_snapshot: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    subtotal: float
    # Product details included - COUPLING!
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentResponse(BaseModel):
    id: int
    amount: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    status: str
    payment_method: str
    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Order Schemas
class OrderCreate(BaseModel):
    """Create order from cart"""
    shipping_address: str
    payment_method: str  # credit_card, paypal, etc.


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    shipping_address: str
    processing_duration_ms: Optional[int] = None  # How long checkout took
    items: List[OrderItemResponse]
    payment: Optional[PaymentResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Simplified order for listing"""
    id: int
    status: OrderStatus
    total_amount: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    item_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Admin endpoint to update order status"""
    status: OrderStatus
