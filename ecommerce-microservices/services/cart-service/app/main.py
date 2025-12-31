"""
Cart Service - Manages shopping carts

This service handles:
- Adding items to cart
- Updating cart quantities
- Removing items from cart
- Getting cart contents
- Clearing cart
"""
import logging
import os
from typing import List
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx

from .database import get_db, init_db
from . import models, schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8004")

# Initialize FastAPI app
app = FastAPI(
    title="Cart Service",
    description="Shopping cart management for E-commerce Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_product_details(product_id: int):
    """Fetch product details from Product Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PRODUCT_SERVICE_URL}/products/{product_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Product not found")
            else:
                raise HTTPException(status_code=503, detail="Product service unavailable")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Product service unavailable")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Cart Service starting up...")
    init_db()
    logger.info("✅ Database initialized")


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Cart Service",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/cart/{user_id}", response_model=schemas.CartResponse)
async def get_cart(user_id: int, db: Session = Depends(get_db)):
    """Get user's shopping cart"""
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

    # Calculate total
    total = sum(float(item.price) * item.quantity for item in cart_items)

    logger.info(f"🛒 Retrieved cart for user {user_id}: {len(cart_items)} items")
    return {
        "items": cart_items,
        "total": f"{total:.2f}"
    }


@app.post("/cart/{user_id}/items", response_model=schemas.CartResponse)
async def add_to_cart(
    user_id: int,
    item_request: schemas.CartItemCreate,
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    # Get product details from Product Service
    product = await get_product_details(item_request.product_id)

    # Check if item already in cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == item_request.product_id
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += item_request.quantity
        db.commit()
        db.refresh(existing_item)
        logger.info(f"✅ Updated cart item: {product['name']} quantity={existing_item.quantity}")
    else:
        # Create new cart item
        cart_item = models.CartItem(
            user_id=user_id,
            product_id=product["id"],
            product_name=product["name"],
            price=Decimal(str(product["price"])),
            quantity=item_request.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        logger.info(f"✅ Added to cart: {product['name']} x{item_request.quantity}")

    # Return updated cart
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    total = sum(float(item.price) * item.quantity for item in cart_items)

    return {
        "items": cart_items,
        "total": f"{total:.2f}"
    }


@app.put("/cart/{user_id}/items/{item_id}", response_model=schemas.CartResponse)
async def update_cart_item(
    user_id: int,
    item_id: int,
    item_update: schemas.CartItemUpdate,
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.user_id == user_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item_update.quantity <= 0:
        # Remove item if quantity is 0 or negative
        db.delete(cart_item)
        logger.info(f"🗑️  Removed from cart: {cart_item.product_name}")
    else:
        cart_item.quantity = item_update.quantity
        logger.info(f"✅ Updated cart: {cart_item.product_name} quantity={item_update.quantity}")

    db.commit()

    # Return updated cart
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    total = sum(float(item.price) * item.quantity for item in cart_items)

    return {
        "items": cart_items,
        "total": f"{total:.2f}"
    }


@app.delete("/cart/{user_id}/items/{item_id}", response_model=schemas.CartResponse)
async def remove_from_cart(
    user_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.user_id == user_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product_name = cart_item.product_name
    db.delete(cart_item)
    db.commit()

    logger.info(f"🗑️  Removed from cart: {product_name}")

    # Return updated cart
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    total = sum(float(item.price) * item.quantity for item in cart_items)

    return {
        "items": cart_items,
        "total": f"{total:.2f}"
    }


@app.delete("/cart/{user_id}", response_model=schemas.CartResponse)
async def clear_cart(user_id: int, db: Session = Depends(get_db)):
    """Clear all items from cart"""
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()

    logger.info(f"🗑️  Cleared cart for user {user_id}")

    return {
        "items": [],
        "total": "0.00"
    }
