"""Order Service Database Models"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base


class Order(Base):
    """
    Order model - stores order data in Order Service's own database.

    NOTE: In microservices, each service owns its data. This Order table
    only contains data relevant to the Order Service, not payment or email status.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_email = Column(String, nullable=False)

    # Order details
    status = Column(String, default="pending")  # pending, confirmed, failed
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Items stored as JSON (denormalized for simplicity in this service)
    items = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Performance tracking (for comparison with monolith)
    processing_duration_ms = Column(Integer, nullable=True)
