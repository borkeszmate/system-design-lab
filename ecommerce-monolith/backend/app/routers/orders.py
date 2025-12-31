"""
Orders Router - THE SLOW ENDPOINT!

The /checkout endpoint demonstrates the monolith nightmare:
- Takes 3-5 seconds to respond
- Blocks on payment processing
- Blocks on email sending
- User must wait for everything
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time

from app.database import get_db
from app.models.user import User
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.utils.auth import get_current_user
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create order from cart and checkout

    ⚠️  WARNING: This endpoint is INTENTIONALLY SLOW! ⚠️

    Expected response time: 3-5 seconds

    Why so slow?
    1. Payment processing: 1 second (external API call)
    2. Email sending: 2 seconds (SMTP server)
    3. Database operations: ~1 second (inventory locking, transactions)

    In microservices:
    - Immediate response with order ID
    - Payment processing in background
    - Email sending in background
    - Event-driven updates

    In our monolith:
    - User waits for EVERYTHING
    - If email server is down, no orders can be created!
    - All other requests to this endpoint are blocked
    """

    print("\n" + "🚨"*40)
    print("🐌 SLOW ENDPOINT ALERT! 🐌")
    print("This will take 3-5 seconds... grab a coffee! ☕")
    print("🚨"*40 + "\n")

    start_time = time.time()

    try:
        order = OrderService.create_order_from_cart(
            db=db,
            user_id=current_user.id,
            shipping_address=order_data.shipping_address,
            payment_method=order_data.payment_method
        )

        elapsed = time.time() - start_time

        print("\n" + "="*80)
        print(f"⏱️  Total response time: {elapsed:.2f} seconds")
        print(f"😢 User had to wait {elapsed:.2f} seconds for their order!")
        print("="*80 + "\n")

        return order

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )


@router.get("/my-orders", response_model=List[OrderListResponse])
def get_my_orders(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's orders

    This is fast! No blocking operations here.
    """
    orders = OrderService.list_user_orders(db, current_user.id, skip, limit)

    # Simplified response
    return [
        {
            "id": order.id,
            "status": order.status,
            "total_amount": order.total_amount,
            "item_count": len(order.items),
            "created_at": order.created_at
        }
        for order in orders
    ]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific order

    Also fast - just reading data
    """
    order = OrderService.get_order(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order
