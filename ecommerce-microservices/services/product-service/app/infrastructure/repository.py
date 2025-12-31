"""Repository pattern for data access"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..domain.models import Product
from ..domain.schemas import ProductCreate, ProductUpdate


class ProductRepository:
    """Product data access repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        return self.db.query(Product).offset(skip).limit(limit).all()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        db_product = Product(**product_data.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update an existing product"""
        db_product = self.get_by_id(product_id)
        if not db_product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)

        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete(self, product_id: int) -> bool:
        """Delete a product"""
        db_product = self.get_by_id(product_id)
        if not db_product:
            return False

        self.db.delete(db_product)
        self.db.commit()
        return True

    def update_stock(self, product_id: int, stock_change: int) -> Optional[Product]:
        """Update product stock"""
        db_product = self.get_by_id(product_id)
        if not db_product:
            return None

        new_stock = db_product.stock + stock_change
        if new_stock < 0:
            raise ValueError("Insufficient stock")

        db_product.stock = new_stock
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
