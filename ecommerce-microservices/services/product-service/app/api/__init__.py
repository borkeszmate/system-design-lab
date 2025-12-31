"""API layer - HTTP routes and handlers"""
from .routes import router
from .dependencies import get_product_service

__all__ = ["router", "get_product_service"]
