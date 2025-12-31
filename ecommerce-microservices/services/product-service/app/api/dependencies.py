"""FastAPI dependencies for dependency injection"""
from fastapi import Depends
from sqlalchemy.orm import Session
from ..infrastructure import get_db, ProductRepository
from ..core import ProductService


def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    """Get product repository instance"""
    return ProductRepository(db)


def get_product_service(repository: ProductRepository = Depends(get_product_repository)) -> ProductService:
    """Get product service instance"""
    return ProductService(repository)
