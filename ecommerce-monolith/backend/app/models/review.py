from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships - TIGHT COUPLING
    # Review depends on both Product and User
    # In microservices, reviews might be a separate service
    # storing only IDs, not database relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review product_id={self.product_id} rating={self.rating}>"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # order_confirmation, shipment, etc.
    message = Column(String, nullable=False)
    read = Column(Integer, default=0)  # 0 = unread, 1 = read (using int for SQLite compatibility)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships - MONOLITH ANTI-PATTERN
    # Notifications are stored in the same DB as everything else
    # In reality, this should be a separate service with its own DB
    # But monolith = everything in one place
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification user_id={self.user_id} type={self.type}>"
