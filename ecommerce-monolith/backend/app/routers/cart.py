"""
Cart Router - Shopping cart management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        # Create cart if it doesn't exist
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Calculate total
    total = sum(item.subtotal for item in cart.items)

    return {
        **cart.__dict__,
        "total": total
    }


@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    # Get user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()

    # Get product
    product = db.query(Product).filter(Product.id == item_data.product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_data.product_id
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += item_data.quantity
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price_snapshot=product.price
        )
        db.add(cart_item)

    db.commit()

    return {"message": "Item added to cart"}


@router.delete("/items/{item_id}")
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )

    db.delete(cart_item)
    db.commit()

    return {"message": "Item removed from cart"}


@router.delete("")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()

    return {"message": "Cart cleared"}
