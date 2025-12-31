# Session 4 - Microservices Architecture Complete! 🚀

**Date:** 2025-12-21
**Duration:** ~2 hours
**Status:** ✅ FULLY FUNCTIONAL MICROSERVICES

---

## What We Built

### Architecture Overview
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────┐
│  API Gateway    │  Port 9000
│  (Entry Point)  │
└──────┬──────────┘
       │
       ├──────────────────────┐
       │                      │
┌──────▼──────┐      ┌────────▼─────┐
│Order Service│      │   RabbitMQ   │
│ Port 8001   │      │  Port 5672   │
│ PostgreSQL  │      │ (Event Bus)  │
│ Port 5433   │      │              │
└──────┬──────┘      └────┬─────┬───┘
       │                  │     │
       └──────────────────┤     │
                          │     │
              ┌───────────▼─┐ ┌─▼──────────┐
              │  Payment    │ │   Email    │
              │  Service    │ │  Service   │
              │  Port 8002  │ │ Port 8003  │
              │  PostgreSQL │ │ (Stateless)│
              │  Port 5434  │ │            │
              └─────────────┘ └────────────┘
```

### Services Created

1. **API Gateway** (Port 9000)
   - Entry point for all client requests
   - Routes to Order Service
   - Returns immediately to user
   - Location: `ecommerce-microservices/api-gateway/`

2. **Order Service** (Port 8001)
   - Creates orders in <20ms
   - Publishes `OrderCreated` events
   - Own PostgreSQL database (port 5433)
   - Location: `ecommerce-microservices/order-service/`

3. **Payment Service** (Port 8002)
   - Consumes `OrderCreated` events
   - Processes payments asynchronously (1s delay)
   - Publishes `PaymentProcessed` events
   - Own PostgreSQL database (port 5434)
   - Location: `ecommerce-microservices/payment-service/`

4. **Email Service** (Port 8003)
   - Consumes `PaymentProcessed` events
   - Sends emails asynchronously (2s delay)
   - Stateless (no database)
   - Location: `ecommerce-microservices/email-service/`

5. **RabbitMQ** (Port 5672, Management: 15672)
   - Message broker for async communication
   - Topic exchange: `ecommerce_events`
   - Routing keys:
     - `order.order.created`
     - `payment.payment.processed`

6. **Supporting Services**
   - MailHog (Port 8026) - Email testing UI
   - PostgreSQL x2 - Separate databases for Order and Payment

---

## Performance Results

### The Dramatic Improvement

| Metric | Monolith | Microservices | Improvement |
|--------|----------|---------------|-------------|
| **Response Time** | 7,600ms | **13ms** | **583x faster!** 🚀 |
| **Payment** | Blocking 1s | Async background | User doesn't wait |
| **Email** | Blocking 2s | Async background | User doesn't wait |
| **Total Backend** | 7,600ms | ~3,000ms (async) | User gets response instantly |

### Real Test Results

**Test Command:**
```bash
curl -X POST http://localhost:9000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{"user_id":1,"user_email":"test@example.com","items":[{"product_id":1,"quantity":1,"price":"1299.99"}]}'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "user_email": "test@example.com",
  "status": "pending",
  "total_amount": "1299.99",
  "items": [...],
  "processing_duration_ms": 13,
  "created_at": "2025-12-21T21:35:38.569861Z"
}
```

**Actual Processing:**
- User response: **13ms** ✅
- Payment processed: 1s later (background)
- Email sent: 2s later (background)
- User never waited for slow operations!

---

## The Async Flow (Event-Driven)

### What Happens When User Clicks Checkout

```
TIME: 0ms
│ User clicks "Checkout"
│
▼
TIME: ~13ms
│ ✅ API Gateway → Order Service
│ ✅ Order created in database
│ ✅ OrderCreated event published to RabbitMQ
│ ✅ USER GETS RESPONSE (13ms total)
│
│ ═══════════════════════════════════════
│ Everything below happens IN BACKGROUND
│ User is already browsing other pages!
│ ═══════════════════════════════════════
│
▼
TIME: ~1000ms (from click)
│ 💳 Payment Service receives OrderCreated event
│ 💳 Processes payment (1s delay simulated)
│ 💳 Saves to payment database
│ 💳 Publishes PaymentProcessed event
│
▼
TIME: ~3000ms (from click)
│ 📧 Email Service receives PaymentProcessed event
│ 📧 Sends confirmation email (2s delay simulated)
│ 📧 Email appears in MailHog
│ ✅ COMPLETE!
│
TOTAL TIME: ~3 seconds
USER WAIT TIME: 13ms (0.4% of monolith time!)
```

---

## All Running Services

### Docker Containers (8 total)

```bash
# Check status
cd /Users/borkeszmate/Sites/system_design/ecommerce-microservices
docker compose ps
```

| Container | Service | Port(s) | Status |
|-----------|---------|---------|--------|
| microservices-gateway | API Gateway | 9000 | Running ✅ |
| microservices-order | Order Service | 8001 | Running ✅ |
| microservices-payment | Payment Service | 8002 | Running ✅ |
| microservices-email | Email Service | 8003 | Running ✅ |
| microservices-rabbitmq | RabbitMQ | 5672, 15672 | Running ✅ |
| microservices-order-db | PostgreSQL | 5433 | Running ✅ |
| microservices-payment-db | PostgreSQL | 5434 | Running ✅ |
| microservices-mailhog | MailHog | 1026, 8026 | Running ✅ |

### URLs to Access

```bash
# API Gateway
http://localhost:9000/health

# Order Service
http://localhost:8001/

# Payment Service
http://localhost:8002/

# Email Service
http://localhost:8003/

# RabbitMQ Management UI
http://localhost:15672/
# Login: ecommerce / ecommerce123

# MailHog (view sent emails)
http://localhost:8026/
```

---

## How to Resume (Next Session)

### 1. Start All Services

```bash
cd /Users/borkeszmate/Sites/system_design/ecommerce-microservices
docker compose up -d
```

Wait 10 seconds for RabbitMQ to be ready, then:

```bash
# Restart services to connect to RabbitMQ
docker compose restart order-service payment-service email-service
```

### 2. Verify Everything is Running

```bash
# Check health
curl http://localhost:9000/health

# Should return:
# {
#   "status": "healthy",
#   "gateway": "operational",
#   "services": {
#     "order-service": "healthy",
#     "payment-service": "healthy",
#     "email-service": "healthy"
#   }
# }
```

### 3. Test the Async Checkout

```bash
curl -X POST http://localhost:9000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{"user_id":2,"user_email":"test2@example.com","items":[{"product_id":1,"quantity":1,"price":"1299.99"}]}'
```

### 4. Watch the Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f payment-service
docker compose logs -f email-service

# See the async flow happen!
```

### 5. View Results

- **Sent Emails:** http://localhost:8026/
- **RabbitMQ Queues:** http://localhost:15672/ (login: ecommerce/ecommerce123)
- **Database:**
  ```bash
  docker exec -it microservices-order-db psql -U order_user -d order_db
  SELECT * FROM orders;
  ```

---

## Key Files & Structure

```
ecommerce-microservices/
├── docker-compose.yml          # All 8 services defined
├── README.md                   # Complete documentation
│
├── api-gateway/
│   ├── app/main.py            # Routes requests to services
│   ├── Dockerfile
│   └── pyproject.toml
│
├── order-service/
│   ├── app/
│   │   ├── main.py            # Order creation + event publishing
│   │   ├── event_publisher.py # RabbitMQ publisher
│   │   ├── models.py          # Order database model
│   │   └── database.py
│   ├── Dockerfile
│   └── pyproject.toml
│
├── payment-service/
│   ├── app/
│   │   ├── main.py            # Starts FastAPI + consumer
│   │   ├── event_consumer.py  # Listens for OrderCreated
│   │   ├── models.py          # Payment database model
│   │   └── database.py
│   ├── Dockerfile
│   └── pyproject.toml
│
├── email-service/
│   ├── app/
│   │   ├── main.py            # Starts FastAPI + consumer
│   │   ├── event_consumer.py  # Listens for PaymentProcessed
│   │   └── email_sender.py    # Sends emails via SMTP
│   ├── Dockerfile
│   └── pyproject.toml
│
└── shared/
    └── events.py               # Event schemas (not used yet)
```

---

## What We Learned

### 1. Event-Driven Architecture
- Services communicate via events, not direct calls
- **OrderCreated** → triggers payment
- **PaymentProcessed** → triggers email
- Loose coupling = services don't know about each other

### 2. Async Processing Benefits
- User gets immediate response
- Slow operations happen in background
- Better user experience
- Can retry failed operations

### 3. Service Isolation
- Each service has its own database
- Order Service: Manages orders
- Payment Service: Manages payments
- Email Service: Stateless, just sends emails
- If email fails, order is still created!

### 4. Message Broker (RabbitMQ)
- Decouples producers from consumers
- Guarantees message delivery
- Enables retry logic
- Supports multiple consumers (scaling)

### 5. Real Performance Gains
- **583x faster** user-perceived speed
- Monolith: 7,600ms blocking
- Microservices: 13ms response
- Background work: ~3 seconds (user doesn't wait)

---

## Comparison: Monolith vs Microservices

### File Structure

**Monolith:**
```
ecommerce-monolith/
└── backend/
    └── app/
        ├── services/
        │   ├── order_service.py     # 11 synchronous steps!
        │   ├── payment_service.py   # 1s blocking
        │   └── email_service.py     # 2s blocking
        └── routers/
            └── orders.py             # Waits for everything
```

**Microservices:**
```
ecommerce-microservices/
├── order-service/               # Returns immediately
├── payment-service/             # Processes async
└── email-service/               # Sends async
```

### Request Flow

**Monolith:**
```
User → API → [Order + Payment + Email] → User
              └─ 7,600ms blocking ─┘
```

**Microservices:**
```
User → API → Order → User (13ms)
              ↓
         RabbitMQ
              ↓
         Payment (1s, background)
              ↓
         RabbitMQ
              ↓
         Email (2s, background)
```

---

## Questions for Next Session

When you return, you mentioned asking about microservice architecture. Here are topics we can explore:

### Completed ✅
- ✅ Event-driven architecture
- ✅ Async processing with message queues
- ✅ Service isolation and independent databases
- ✅ RabbitMQ basics

### Can Explore Next 🎯

1. **Scaling Microservices**
   - Run multiple instances of services
   - Load balancing
   - Horizontal vs vertical scaling

2. **Advanced Patterns**
   - Circuit breaker (handle failures)
   - Retry logic with exponential backoff
   - Dead-letter queues
   - Saga pattern for distributed transactions

3. **Observability**
   - Distributed tracing (follow request across services)
   - Centralized logging
   - Metrics and monitoring

4. **Service Discovery**
   - How services find each other
   - Dynamic vs static configuration

5. **API Gateway Advanced**
   - Rate limiting
   - Authentication/Authorization
   - Request transformation
   - Caching

6. **Database Patterns**
   - Event sourcing
   - CQRS (Command Query Responsibility Segregation)
   - Eventual consistency handling

7. **Testing Microservices**
   - Integration tests
   - Contract testing
   - End-to-end tests

8. **Deployment**
   - Kubernetes basics
   - Service mesh (Istio, Linkerd)
   - Blue-green deployments
   - Canary releases

---

## Stopping Services

```bash
cd /Users/borkeszmate/Sites/system_design/ecommerce-microservices

# Stop all services
docker compose down

# Stop and remove volumes (clean databases)
docker compose down -v
```

---

## Quick Commands Reference

```bash
# Start everything
docker compose up -d

# View logs
docker compose logs -f

# Restart a service
docker compose restart order-service

# Check status
docker compose ps

# Test checkout
curl -X POST http://localhost:9000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{"user_id":1,"user_email":"test@example.com","items":[{"product_id":1,"quantity":1,"price":"99.99"}]}'

# View RabbitMQ queues
open http://localhost:15672/

# View sent emails
open http://localhost:8026/
```

---

## Stats

- **Lines of Code:** ~800 (across 4 services)
- **Docker Containers:** 8
- **Databases:** 2 (PostgreSQL)
- **Message Broker:** RabbitMQ
- **Events:** 2 types (OrderCreated, PaymentProcessed)
- **Response Time:** 13ms (vs 7600ms monolith)
- **Improvement:** 583x faster!

---

## Next Phase Suggestions

### Phase 3: Scalability & Performance
- Run multiple instances of services
- Implement caching (Redis)
- Add load balancer
- Performance testing with load

### Alternative: Deep Dive into Current Setup
- Add circuit breakers
- Implement retry logic
- Add distributed tracing
- Centralized logging
- Better error handling

---

**Session Status:** ✅ COMPLETE
**Achievement Unlocked:** Built Event-Driven Microservices! 🏆
**Ready for:** Phase 3 or deep dive into microservices patterns

**Welcome back message for next session:**
"Your microservices are in `ecommerce-microservices/`. Run `docker compose up -d` to start. Ask me about scaling, observability, or any microservices pattern!"
