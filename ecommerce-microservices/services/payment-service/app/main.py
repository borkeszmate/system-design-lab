"""
Payment Service - Main Application

This service runs a RabbitMQ consumer in the background to process payments asynchronously.
It also runs a simple FastAPI server for health checks.
"""
import logging
import threading
from fastapi import FastAPI
from .database import Base, engine
from .event_consumer import PaymentEventConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app (for health checks)
app = FastAPI(
    title="Payment Service",
    description="Microservices Payment Service - Processes payments asynchronously",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Payment Service",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Consuming OrderCreated events, processing payments asynchronously"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "payment-service",
        "consumer": "running"
    }


def start_consumer():
    """Start the RabbitMQ consumer in a separate thread"""
    consumer = PaymentEventConsumer()
    try:
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"❌ Consumer failed: {e}")


if __name__ == "__main__":
    import uvicorn

    # Start RabbitMQ consumer in background thread
    logger.info("🚀 Starting Payment Service...")
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logger.info("✅ RabbitMQ consumer started in background")

    # Start FastAPI server
    logger.info("✅ Starting FastAPI server on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
