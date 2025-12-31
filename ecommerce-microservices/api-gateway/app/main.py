"""
API Gateway - Entry Point for Microservices

This gateway routes requests to appropriate microservices.
In production, it would also handle:
- Rate limiting
- Request/Response transformation
- Caching
- Load balancing
"""
import logging
import os
import httpx
from typing import List
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8005")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8004")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart-service:8006")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8001")

security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce API Gateway",
    description="API Gateway for Microservices E-commerce Platform",
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


# Helper function to extract user ID from token
async def get_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user ID from JWT token by calling User Service"""
    token = credentials.credentials
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                user_data = response.json()
                return user_data["id"]
            else:
                raise HTTPException(status_code=401, detail="Invalid authentication")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="User service unavailable")


@app.get("/")
async def root():
    """Gateway health check"""
    return {
        "service": "API Gateway",
        "status": "healthy",
        "version": "1.0.0",
        "architecture": "Microservices",
        "services": {
            "user": USER_SERVICE_URL,
            "product": PRODUCT_SERVICE_URL,
            "cart": CART_SERVICE_URL,
            "order": ORDER_SERVICE_URL,
        }
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "gateway": "operational",
        "services": {
            "user-service": "healthy",
            "product-service": "healthy",
            "cart-service": "healthy",
            "order-service": "healthy",
            "payment-service": "healthy",
            "email-service": "healthy"
        }
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS - Forward to User Service
# ============================================================================

@app.post("/api/auth/login")
async def login(request: dict):
    """Login - forwards to User Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_SERVICE_URL}/auth/login",
                json=request,
                timeout=10.0
            )
            if response.status_code == 200:
                logger.info(f"✅ User logged in via User Service")
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Login failed"))
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to User Service: {e}")
        raise HTTPException(status_code=503, detail="User Service unavailable")


@app.get("/api/auth/me")
async def get_current_user_info(authorization: str = Header(None)):
    """Get current user profile - forwards to User Service"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/me",
                headers={"Authorization": authorization},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to get user info")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to User Service: {e}")
        raise HTTPException(status_code=503, detail="User Service unavailable")


# ============================================================================
# PRODUCTS ENDPOINTS - Forward to Product Service
# ============================================================================

@app.get("/api/products")
async def get_products():
    """Get all products - forwards to Product Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PRODUCT_SERVICE_URL}/products",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch products")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Product Service: {e}")
        raise HTTPException(status_code=503, detail="Product Service unavailable")


@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Get product by ID - forwards to Product Service"""
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
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch product")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Product Service: {e}")
        raise HTTPException(status_code=503, detail="Product Service unavailable")


# ============================================================================
# CART ENDPOINTS - Forward to Cart Service
# ============================================================================

@app.get("/api/cart")
async def get_cart(user_id: int = Depends(get_user_id_from_token)):
    """Get user's cart - forwards to Cart Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CART_SERVICE_URL}/cart/{user_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch cart")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Cart Service: {e}")
        raise HTTPException(status_code=503, detail="Cart Service unavailable")


@app.post("/api/cart/items")
async def add_to_cart(request: dict, user_id: int = Depends(get_user_id_from_token)):
    """Add item to cart - forwards to Cart Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CART_SERVICE_URL}/cart/{user_id}/items",
                json=request,
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info(f"✅ Added to cart for user {user_id}")
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to add to cart")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Cart Service: {e}")
        raise HTTPException(status_code=503, detail="Cart Service unavailable")


@app.put("/api/cart/items/{item_id}")
async def update_cart_item(item_id: int, request: dict, user_id: int = Depends(get_user_id_from_token)):
    """Update cart item - forwards to Cart Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CART_SERVICE_URL}/cart/{user_id}/items/{item_id}",
                json=request,
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to update cart")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Cart Service: {e}")
        raise HTTPException(status_code=503, detail="Cart Service unavailable")


@app.delete("/api/cart/items/{item_id}")
async def remove_from_cart(item_id: int, user_id: int = Depends(get_user_id_from_token)):
    """Remove item from cart - forwards to Cart Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CART_SERVICE_URL}/cart/{user_id}/items/{item_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to remove from cart")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Cart Service: {e}")
        raise HTTPException(status_code=503, detail="Cart Service unavailable")


@app.delete("/api/cart")
async def clear_cart(user_id: int = Depends(get_user_id_from_token)):
    """Clear cart - forwards to Cart Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CART_SERVICE_URL}/cart/{user_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to clear cart")
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Cart Service: {e}")
        raise HTTPException(status_code=503, detail="Cart Service unavailable")


# ============================================================================
# ORDER ENDPOINTS - Forward to Order Service
# ============================================================================

@app.post("/api/checkout")
async def checkout(request: CheckoutRequest):
    """
    Checkout endpoint - forwards to Order Service.

    This is where the magic happens:
    - Request comes to gateway
    - Forwarded to Order Service
    - Order Service creates order and publishes event (~300-500ms)
    - Gateway returns response to user IMMEDIATELY
    - Payment and email happen asynchronously in the background!
    """
    logger.info("=" * 80)
    logger.info("🌐 [API Gateway] Received checkout request")
    logger.info(f"👤 User: {request.user_email} | Items: {len(request.items)}")
    logger.info("📤 Forwarding to Order Service...")
    logger.info("=" * 80)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ORDER_SERVICE_URL}/checkout",
                json=request.model_dump(mode='json'),
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                logger.info("=" * 80)
                logger.info(f"✅ Order created successfully! Order ID: {data['id']}")
                logger.info(f"⏱️  Response time: {data['processing_duration_ms']}ms")
                logger.info("🎉 User got immediate response!")
                logger.info("=" * 80)
                return data
            else:
                logger.error(f"❌ Order Service returned error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Order creation failed")

    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Order Service: {e}")
        raise HTTPException(status_code=503, detail="Order Service unavailable")


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    """Get order by ID - forwards to Order Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ORDER_SERVICE_URL}/orders/{order_id}",
                timeout=5.0
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Order not found")
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch order")

    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Order Service: {e}")
        raise HTTPException(status_code=503, detail="Order Service unavailable")


@app.get("/api/orders/{order_id}/status")
async def get_order_status(order_id: int):
    """
    Get real-time order status - forwards to Order Service
    Used for polling order status updates
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ORDER_SERVICE_URL}/orders/{order_id}",
                timeout=5.0
            )

            if response.status_code == 200:
                order_data = response.json()
                return {
                    "id": order_data["id"],
                    "status": order_data["status"],
                    "payment": order_data.get("payment")
                }
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Order not found")
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch order status")

    except httpx.RequestError as e:
        logger.error(f"❌ Failed to connect to Order Service: {e}")
        raise HTTPException(status_code=503, detail="Order Service unavailable")
