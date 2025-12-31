"""
Order Service - FastAPI Application

This service handles order creation and publishes events to RabbitMQ.

KEY DIFFERENCE FROM MONOLITH:
- Checkout takes <500ms (vs 7600ms in monolith)
- Payment processed asynchronously
- Email sent asynchronously
- User doesn't wait for slow operations!
"""
import time
import uuid
import logging
from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Order
from .event_publisher import event_publisher
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Order Service",
    description="Microservices Order Service - Creates orders quickly and publishes events",
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


# Pydantic schemas
class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int
    price: Decimal


class CheckoutRequest(BaseModel):
    user_id: int
    user_email: str
    items: List[OrderItemRequest]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    status: str
    total_amount: Decimal
    items: List[dict]
    processing_duration_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


# Startup event - connect to RabbitMQ
@app.on_event("startup")
async def startup_event():
    """Connect to RabbitMQ on startup"""
    try:
        event_publisher.connect()
        logger.info("🚀 Order Service started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start Order Service: {e}")


# Shutdown event - close RabbitMQ connection
@app.on_event("shutdown")
async def shutdown_event():
    """Close RabbitMQ connection on shutdown"""
    event_publisher.close()
    logger.info("🛑 Order Service shutting down")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Order Service",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/checkout", response_model=OrderResponse)
async def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    """
    Create an order and publish event to RabbitMQ.

    THIS IS THE KEY MICROSERVICES IMPROVEMENT:
    - Creates order in database (~100-200ms)
    - Publishes event to RabbitMQ (~10-50ms)
    - Returns IMMEDIATELY to user (~300-500ms total)
    - Payment and email happen ASYNCHRONOUSLY

    vs Monolith:
    - Creates order, processes payment, sends email ALL synchronously (7600ms)
    - User waits for EVERYTHING
    """
    start_time = time.time()

    logger.info("=" * 80)
    logger.info("🛒 [Order Service] Starting ASYNC order creation...")
    logger.info("⚡ This will return in <500ms (payment & email happen in background)")
    logger.info("=" * 80)

    # Step 1: Calculate total
    logger.info("[Step 1/4] Calculating total amount...")
    total_amount = sum(item.price * item.quantity for item in request.items)

    # Step 2: Create order in database
    logger.info("[Step 2/4] Creating order in database...")
    order = Order(
        user_id=request.user_id,
        user_email=request.user_email,
        status="pending",  # Will be updated when payment completes
        total_amount=total_amount,
        items=[item.model_dump(mode='json') for item in request.items]
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    logger.info(f"✅ Order #{order.id} created in database")

    # Step 3: Publish event to RabbitMQ
    logger.info("[Step 3/4] Publishing OrderCreated event to RabbitMQ...")

    event_data = {
        "event_type": "order.created",
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "order_id": order.id,
        "user_id": order.user_id,
        "user_email": order.user_email,
        "total_amount": str(order.total_amount),
        "items": order.items
    }

    try:
        event_publisher.publish_event(
            routing_key="order.order.created",
            event_data=event_data
        )
        logger.info("✅ Event published! Payment Service will process it asynchronously")
    except Exception as e:
        logger.error(f"❌ Failed to publish event: {e}")
        # In production, you might want to retry or use a dead-letter queue
        # For now, we'll still return success since order is created

    # Step 4: Calculate duration and return
    duration_ms = int((time.time() - start_time) * 1000)
    order.processing_duration_ms = duration_ms
    db.commit()

    logger.info("[Step 4/4] Returning response to user...")
    logger.info("=" * 80)
    logger.info(f"⏱️  Total response time: {duration_ms}ms")
    logger.info("🎉 User gets immediate response! Payment & email happen in background")
    logger.info("=" * 80)

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        user_email=order.user_email,
        status=order.status,
        total_amount=order.total_amount,
        items=order.items,
        processing_duration_ms=duration_ms,
        created_at=order.created_at
    )


@app.get("/orders/{order_id}")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        user_email=order.user_email,
        status=order.status,
        total_amount=order.total_amount,
        items=order.items,
        processing_duration_ms=order.processing_duration_ms or 0,
        created_at=order.created_at
    )


@app.get("/orders/user/{user_id}")
async def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """Get all orders for a user"""
    orders = db.query(Order).filter(Order.user_id == user_id).all()

    return [
        OrderResponse(
            id=order.id,
            user_id=order.user_id,
            user_email=order.user_email,
            status=order.status,
            total_amount=order.total_amount,
            items=order.items,
            processing_duration_ms=order.processing_duration_ms or 0,
            created_at=order.created_at
        )
        for order in orders
    ]
