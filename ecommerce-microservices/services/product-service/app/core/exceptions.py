"""Custom exceptions for Product Service"""


class ProductNotFoundException(Exception):
    """Raised when a product is not found"""
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found")


class InsufficientStockException(Exception):
    """Raised when there's insufficient stock"""
    def __init__(self, product_id: int, requested: int, available: int):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product {product_id}. "
            f"Requested: {requested}, Available: {available}"
        )
