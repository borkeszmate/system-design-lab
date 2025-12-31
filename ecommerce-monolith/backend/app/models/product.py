from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships - TIGHT COUPLING EXAMPLE
    # Product is directly coupled to:
    # - Category (acceptable)
    # - Inventory (should be separate service!)
    # - CartItems (should be separate service!)
    # - OrderItems (should be separate service!)
    # - Reviews (should be separate service!)
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)  # For pending orders
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="inventory")

    @property
    def available(self):
        """Available inventory = total - reserved"""
        return self.quantity - self.reserved_quantity

    def __repr__(self):
        return f"<Inventory product_id={self.product_id} available={self.available}>"
