"""
Product Service - Clean Architecture Implementation

This service follows best practices:
- Layered Architecture (API, Core, Domain, Infrastructure)
- Repository Pattern for data access
- Service Layer for business logic
- Dependency Injection via FastAPI
- Proper error handling and logging
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .infrastructure import init_db, get_db
from .domain import Product
from .api import router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Product catalog management for E-commerce Platform",
    version=settings.APP_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data on startup"""
    logger.info(f"🚀 {settings.APP_NAME} starting up...")
    init_db()
    logger.info("✅ Database initialized")

    # Seed initial products if database is empty
    db = next(get_db())
    product_count = db.query(Product).count()
    if product_count == 0:
        logger.info("📦 Seeding initial products...")
        initial_products = [
            Product(
                name="Gaming Laptop",
                description="High-performance laptop for gaming and development",
                price=1299.99,
                stock=10
            ),
            Product(
                name="Wireless Mouse",
                description="Ergonomic wireless mouse with precision tracking",
                price=49.99,
                stock=50
            ),
            Product(
                name="Mechanical Keyboard",
                description="RGB mechanical keyboard with custom switches",
                price=149.99,
                stock=25
            ),
        ]
        db.add_all(initial_products)
        db.commit()
        logger.info("✅ Initial products seeded")


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": settings.APP_NAME,
        "status": "healthy",
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
