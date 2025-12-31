from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Order status enum - shows the entire lifecycle in one service"""
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    shipping_address = Column(String, nullable=False)
    processing_duration_ms = Column(Integer, nullable=True)  # How long checkout took (milliseconds)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships - MAXIMUM COUPLING!
    # Order is the "God Object" that ties everything together:
    # - User (who placed it)
    # - OrderItems (what was ordered) -> Products
    # - Payment (how it was paid)
    # This is a classic monolith anti-pattern
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)

    def __repr__(self):
        return f"<Order id={self.id} status={self.status} total={self.total_amount}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_snapshot = Column(Numeric(10, 2), nullable=False)  # Price at time of order
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships - COUPLING ACROSS DOMAINS
    # OrderItem knows about both Order and Product
    # In microservices, we'd store product_id but not have a direct relationship
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    @property
    def subtotal(self):
        """Calculate subtotal for this order item"""
        return float(self.price_snapshot) * self.quantity

    def __repr__(self):
        return f"<OrderItem order_id={self.order_id} product_id={self.product_id}>"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False)  # pending, completed, failed
    payment_method = Column(String, nullable=False)  # credit_card, paypal, etc.
    transaction_id = Column(String, unique=True)  # External payment gateway ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships - TIGHT COUPLING
    # Payment is tightly bound to Order
    # In reality, payment service should be separate
    # But in monolith, we have direct DB relationship
    order = relationship("Order", back_populates="payment")

    def __repr__(self):
        return f"<Payment order_id={self.order_id} status={self.status}>"
