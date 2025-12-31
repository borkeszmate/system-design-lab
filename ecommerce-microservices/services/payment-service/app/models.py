"""Payment Service Database Models"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from .database import Base


class Payment(Base):
    """
    Payment model - stores payment data in Payment Service's own database.

    This service owns payment data. Order Service doesn't need to know
    about payment details - they communicate via events.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)

    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")  # pending, completed, failed
    transaction_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
