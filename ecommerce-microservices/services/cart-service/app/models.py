"""Database models for Cart Service"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, ForeignKey
from .database import Base


class CartItem(Base):
    """Cart Item model"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CartItem(id={self.id}, user_id={self.user_id}, product={self.product_name}, qty={self.quantity})>"
