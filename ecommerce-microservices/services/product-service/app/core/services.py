"""Business logic for Product Service"""
import logging
from typing import List
from ..infrastructure.repository import ProductRepository
from ..domain.schemas import ProductCreate, ProductUpdate, ProductResponse
from .exceptions import ProductNotFoundException, InsufficientStockException

logger = logging.getLogger(__name__)


class ProductService:
    """Product business logic"""

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def get_all_products(self, skip: int = 0, limit: int = 100) -> List[ProductResponse]:
        """Get all products"""
        products = self.repository.get_all(skip, limit)
        logger.info(f"Retrieved {len(products)} products")
        return [ProductResponse.model_validate(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        """Get product by ID"""
        product = self.repository.get_by_id(product_id)
        if not product:
            logger.warning(f"Product {product_id} not found")
            raise ProductNotFoundException(product_id)

        logger.info(f"Retrieved product: {product.name}")
        return ProductResponse.model_validate(product)

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create a new product"""
        product = self.repository.create(product_data)
        logger.info(f"Created product: {product.name} (ID: {product.id})")
        return ProductResponse.model_validate(product)

    def update_product(self, product_id: int, product_data: ProductUpdate) -> ProductResponse:
        """Update a product"""
        product = self.repository.update(product_id, product_data)
        if not product:
            raise ProductNotFoundException(product_id)

        logger.info(f"Updated product: {product.name} (ID: {product.id})")
        return ProductResponse.model_validate(product)

    def delete_product(self, product_id: int) -> None:
        """Delete a product"""
        success = self.repository.delete(product_id)
        if not success:
            raise ProductNotFoundException(product_id)

        logger.info(f"Deleted product ID: {product_id}")

    def update_stock(self, product_id: int, stock_change: int) -> ProductResponse:
        """Update product stock"""
        try:
            product = self.repository.update_stock(product_id, stock_change)
            if not product:
                raise ProductNotFoundException(product_id)

            logger.info(f"Updated stock for {product.name}: {product.stock}")
            return ProductResponse.model_validate(product)
        except ValueError as e:
            product = self.repository.get_by_id(product_id)
            raise InsufficientStockException(
                product_id,
                abs(stock_change),
                product.stock if product else 0
            )
