"""
Products Router - Basic CRUD for products
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.product import Product, Category, Inventory
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    CategoryCreate,
    CategoryResponse
)
from app.utils.auth import get_current_admin_user

router = APIRouter()


# Categories
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new category (admin only)"""
    category = Category(**category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    return db.query(Category).all()


# Products
@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new product with initial inventory (admin only)"""
    # Create product
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.category_id,
        image_url=product_data.image_url
    )
    db.add(product)
    db.flush()

    # Create inventory
    inventory = Inventory(
        product_id=product.id,
        quantity=product_data.initial_inventory,
        reserved_quantity=0
    )
    db.add(inventory)
    db.commit()
    db.refresh(product)

    return product


@router.get("", response_model=List[ProductResponse])
def list_products(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all products"""
    products = db.query(Product).offset(skip).limit(limit).all()

    # Add inventory info to response
    response_products = []
    for product in products:
        product_dict = {
            **product.__dict__,
            "available_stock": product.inventory.available if product.inventory else 0
        }
        response_products.append(product_dict)

    return response_products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {
        **product.__dict__,
        "available_stock": product.inventory.available if product.inventory else 0
    }
