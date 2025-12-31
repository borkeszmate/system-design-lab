"""
Email Service - Main Application

This service runs a RabbitMQ consumer to send emails asynchronously.
"""
import logging
import threading
from fastapi import FastAPI
from .event_consumer import EmailEventConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app (for health checks)
app = FastAPI(
    title="Email Service",
    description="Microservices Email Service - Sends emails asynchronously",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Email Service",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Consuming PaymentProcessed events, sending emails asynchronously"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "email-service",
        "consumer": "running"
    }


def start_consumer():
    """Start the RabbitMQ consumer in a separate thread"""
    consumer = EmailEventConsumer()
    try:
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"❌ Consumer failed: {e}")


if __name__ == "__main__":
    import uvicorn

    # Start RabbitMQ consumer in background thread
    logger.info("🚀 Starting Email Service...")
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logger.info("✅ RabbitMQ consumer started in background")

    # Start FastAPI server
    logger.info("✅ Starting FastAPI server on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
