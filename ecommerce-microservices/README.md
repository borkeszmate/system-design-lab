# E-commerce Microservices Architecture

This is a microservices implementation of the e-commerce platform, demonstrating how to achieve **<500ms response times** compared to the **7.6 second** monolith checkout.

📖 **For local development setup with VS Code workspace, see [DEVELOPMENT.md](./DEVELOPMENT.md)**

## Architecture Overview

```
┌─────────────┐
│   Frontend  │
│  (Port 3000)│
└──────┬──────┘
       │
┌──────▼──────────┐
│  API Gateway    │
│  (Port 9000)    │
└──────┬──────────┘
       │
       ├──────────────┐
       │              │
┌──────▼──────┐  ┌───▼───────┐
│Order Service│  │  RabbitMQ │
│ (Port 8001) │  │(Port 5672)│
└──────┬──────┘  └─────┬─────┘
       │               │
       └───────────────┼────────┐
                       │        │
              ┌────────▼──┐  ┌──▼────────┐
              │  Payment  │  │   Email   │
              │  Service  │  │  Service  │
              │(Port 8002)│  │(Port 8003)│
              └───────────┘  └───────────┘
```

## Services

### 1. API Gateway (Port 9000)
- Entry point for all client requests
- Routes requests to appropriate services
- Returns immediately to client

### 2. Order Service (Port 8001)
- Creates orders quickly (~300ms)
- Publishes `OrderCreated` events to RabbitMQ
- Own PostgreSQL database (port 5433)

### 3. Payment Service (Port 8002)
- Listens for `OrderCreated` events
- Processes payments asynchronously (1s delay)
- Publishes `PaymentProcessed` events
- Own PostgreSQL database (port 5434)

### 4. Email Service (Port 8003)
- Listens for `PaymentProcessed` events
- Sends confirmation emails asynchronously (2s delay)
- Stateless (no database)

### 5. RabbitMQ (Port 5672, Management UI: 15672)
- Message broker for async communication
- Topic exchange for flexible routing
- Durable queues for reliability

## Quick Start

### 1. Build and Start All Services

```bash
cd ecommerce-microservices
docker compose up --build
```

This will start:
- RabbitMQ
- PostgreSQL (2 instances for Order & Payment services)
- MailHog
- API Gateway
- Order Service
- Payment Service
- Email Service

### 2. Check Service Health

```bash
# API Gateway
curl http://localhost:9000/health

# Order Service
curl http://localhost:8001

# Payment Service
curl http://localhost:8002

# Email Service
curl http://localhost:8003

# RabbitMQ Management UI
open http://localhost:15672
# Login: ecommerce / ecommerce123
```

### 3. Test Async Checkout

```bash
curl -X POST http://localhost:9000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "user_email": "test@example.com",
    "items": [
      {
        "product_id": 1,
        "quantity": 1,
        "price": "1299.99"
      }
    ]
  }'
```

**Expected Result:**
- Response in **<500ms** ⚡
- Order created
- Payment processes in background (1s)
- Email sent in background (2s)
- User doesn't wait for payment or email!

## The Async Flow

### Monolith (Old):
```
User → API → Create Order + Process Payment + Send Email (7.6s) → User
              ↑____________ALL BLOCKING____________↑
```

### Microservices (New):
```
User → API Gateway → Order Service (300ms) → User ✅
                          ↓ (publishes event)
                     RabbitMQ
                          ↓
                   Payment Service (1s, background)
                          ↓ (publishes event)
                     RabbitMQ
                          ↓
                   Email Service (2s, background)
```

**Total user wait: ~300-500ms** (vs 7600ms in monolith!)

## Performance Comparison

| Metric | Monolith | Microservices | Improvement |
|--------|----------|---------------|-------------|
| Response Time | 7,600ms | <500ms | **15x faster** |
| User Waits For | Everything | Just order creation | **Huge UX win** |
| Payment | Blocking | Async (background) | Non-blocking |
| Email | Blocking | Async (background) | Non-blocking |
| Database | Single shared | Per-service | Better isolation |
| Scaling | All-or-nothing | Independent | More efficient |

## Monitoring

### RabbitMQ Management UI
- URL: http://localhost:15672
- Username: `ecommerce`
- Password: `ecommerce123`
- View queues, exchanges, message rates

### MailHog (Email Viewer)
- URL: http://localhost:8026
- View sent confirmation emails

### Service Logs

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f order-service
docker compose logs -f payment-service
docker compose logs -f email-service
```

## Database Access

### Order Service Database
```bash
docker exec -it microservices-order-db psql -U order_user -d order_db

# Query orders
SELECT id, user_email, status, total_amount, processing_duration_ms
FROM orders
ORDER BY created_at DESC;
```

### Payment Service Database
```bash
docker exec -it microservices-payment-db psql -U payment_user -d payment_db

# Query payments
SELECT id, order_id, amount, status, transaction_id
FROM payments
ORDER BY created_at DESC;
```

## Event Flow

1. **OrderCreated Event**
   - Published by: Order Service
   - Consumed by: Payment Service
   - Routing key: `order.order.created`
   - Queue: `payment_service_queue`

2. **PaymentProcessed Event**
   - Published by: Payment Service
   - Consumed by: Email Service
   - Routing key: `payment.payment.processed`
   - Queue: `email_service_queue`

## Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean database)
docker compose down -v
```

## Development

For comprehensive local development setup including:
- VS Code multi-root workspace configuration
- Poetry dependency management
- Running services without Docker
- Adding new microservices
- Troubleshooting

**See the detailed [DEVELOPMENT.md](./DEVELOPMENT.md) guide.**

## Key Learnings

### Benefits of Microservices
1. **Fast Response Times**: User gets response in <500ms
2. **Independent Scaling**: Scale email service without touching order service
3. **Fault Isolation**: Email failure doesn't fail the order
4. **Technology Freedom**: Each service can use different tech stack
5. **Independent Deployment**: Deploy payment service without redeploying everything

### Trade-offs
1. **Complexity**: More moving parts to manage
2. **Eventual Consistency**: Order created before payment processed
3. **Distributed Tracing**: Need to track requests across services
4. **Network Latency**: Services communicate over network

### Best Practices Demonstrated
- Event-driven architecture for async operations
- Service-owned databases (no shared database)
- Health check endpoints
- Durable message queues
- Idempotent event consumers
- Structured logging

## Next Steps

1. Add distributed tracing (Jaeger, Zipkin)
2. Implement retry logic and dead-letter queues
3. Add API Gateway authentication
4. Implement circuit breakers
5. Add metrics and monitoring (Prometheus, Grafana)
6. Scale services horizontally (multiple instances)
7. Add integration tests

---

**Status**: ✅ Fully Functional Microservices Architecture
**Comparison**: Run both monolith and microservices to see the difference!
