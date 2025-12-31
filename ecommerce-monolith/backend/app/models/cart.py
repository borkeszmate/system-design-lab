from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships - TIGHT COUPLING!
    # Cart directly depends on User and CartItems
    # This makes it hard to separate cart service from user service
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart user_id={self.user_id} items={len(self.items)}>"


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price_snapshot = Column(Numeric(10, 2), nullable=False)  # Price at time of adding
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships - MORE TIGHT COUPLING!
    # CartItem needs both Cart AND Product
    # This creates dependencies across multiple domains
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return float(self.price_snapshot) * self.quantity

    def __repr__(self):
        return f"<CartItem product_id={self.product_id} qty={self.quantity}>"
