# Import all models so SQLAlchemy registers them
# This is important for migrations and table creation

from app.models.user import User, UserRole
from app.models.product import Category, Product, Inventory
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, Payment, OrderStatus
from app.models.review import Review, Notification

# Export all models
__all__ = [
    # User models
    "User",
    "UserRole",
    # Product models
    "Category",
    "Product",
    "Inventory",
    # Cart models
    "Cart",
    "CartItem",
    # Order models
    "Order",
    "OrderItem",
    "Payment",
    "OrderStatus",
    # Review and Notification models
    "Review",
    "Notification",
]
