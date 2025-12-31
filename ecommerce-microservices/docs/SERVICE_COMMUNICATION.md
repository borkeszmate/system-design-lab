# How Microservices Communicate: Complete Guide

## Overview: Two Communication Patterns in Your System

### 1. Synchronous (Request-Response)
**Used by:** API Gateway → Order Service

```
Client → API Gateway → Order Service → Response
         (HTTP)        (HTTP)
```

**Characteristics:**
- Waits for response
- Direct connection
- Fast and simple
- Coupled: Gateway needs to know Order Service URL

### 2. Asynchronous (Event-Driven)
**Used by:** Order → Payment → Email

```
Order Service → RabbitMQ → Payment Service
                  ↓
                RabbitMQ → Email Service
```

**Characteristics:**
- No waiting for response
- No direct connection
- Services don't know about each other
- Decoupled: Services only know about events

---

## The Complete Flow: What Happens When You Checkout

Let me trace through your actual code step by step:

### Step 1: Client → API Gateway (HTTP)

**Client Request:**
```bash
curl -X POST http://localhost:9000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{"user_id":1,"user_email":"test@example.com","items":[...]}'
```

**API Gateway receives this** at `api-gateway/app/main.py:87`

```python
@app.post("/api/checkout")
async def checkout(request: CheckoutRequest):
    logger.info("🌐 [API Gateway] Received checkout request")
    # Gateway acts as a router - forwards to Order Service
```

---

### Step 2: API Gateway → Order Service (HTTP)

**API Gateway forwards** at `api-gateway/app/main.py:105-110`

```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{ORDER_SERVICE_URL}/checkout",  # http://order-service:8001
        json=request.model_dump(mode='json'),
        timeout=10.0
    )
```

**This is synchronous HTTP communication:**
```
API Gateway (port 9000)
    │
    │ HTTP POST
    │ http://order-service:8001/checkout
    ↓
Order Service (port 8001)
```

---

### Step 3: Order Service Processes (Fast!)

**Order Service** at `order-service/app/main.py:118-147`

```python
@app.post("/checkout", response_model=OrderResponse)
async def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    start_time = time.time()

    # Step 1: Calculate total (~1ms)
    total_amount = sum(item.price * item.quantity for item in request.items)

    # Step 2: Create order in database (~10ms)
    order = Order(
        user_id=request.user_id,
        user_email=request.user_email,
        status="pending",
        total_amount=total_amount,
        items=[item.model_dump(mode='json') for item in request.items]
    )
    db.add(order)
    db.commit()

    # Step 3: Publish event to RabbitMQ (~2ms)
    # THIS IS WHERE ASYNC MAGIC HAPPENS! 🎯
```

**Total time: ~13ms** ⚡

---

### Step 4: Order Service → RabbitMQ (Event Publishing)

**This is the KEY to async communication!**

**Order Service publishes event** at `order-service/app/main.py:154-163`

```python
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

event_publisher.publish_event(
    routing_key="order.order.created",  # This determines who gets it
    event_data=event_data
)
```

**Under the hood** at `order-service/app/event_publisher.py:49-64`

```python
def publish_event(self, routing_key: str, event_data: Dict[str, Any]):
    message = json.dumps(event_data, default=str)

    # Publish to RabbitMQ exchange
    self.channel.basic_publish(
        exchange=self.exchange_name,      # "ecommerce_events"
        routing_key=routing_key,          # "order.order.created"
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent (survives RabbitMQ restart)
            content_type='application/json'
        )
    )
```

---

### Step 5: RabbitMQ Routes the Event

**What RabbitMQ does:**

```
┌──────────────────────────────────────────────┐
│            RabbitMQ Exchange                 │
│            "ecommerce_events"                │
│            Type: topic                       │
├──────────────────────────────────────────────┤
│                                              │
│  Receives event:                             │
│    routing_key: "order.order.created"        │
│    body: { order_id: 1, user_email: ... }   │
│                                              │
│  Routing logic:                              │
│  ┌────────────────────────────────────┐     │
│  │ Queue: payment_service_queue       │     │
│  │ Binding: "order.order.created"     │     │
│  │ Match? ✅ YES                      │     │
│  │ Action: Send event to this queue   │     │
│  └────────────────────────────────────┘     │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │ Queue: email_service_queue         │     │
│  │ Binding: "payment.payment.processed"│    │
│  │ Match? ❌ NO                       │     │
│  │ Action: Don't send event here      │     │
│  └────────────────────────────────────┘     │
└──────────────────────────────────────────────┘
```

**Key concepts:**
- **Exchange**: Routes messages based on routing keys
- **Queue**: Holds messages for a specific service
- **Binding**: Rule that says "Queue X wants messages with routing key Y"
- **Routing Key**: Like an address - determines where message goes

---

### Step 6: Payment Service Receives Event

**Payment Service is listening** at `payment-service/app/event_consumer.py:30-56`

```python
class PaymentEventConsumer:
    def __init__(self):
        self.queue_name = "payment_service_queue"
        self.routing_key = "order.order.created"  # I want these events!

    def connect(self):
        # Declare queue
        self.channel.queue_declare(queue=self.queue_name, durable=True)

        # Bind queue to exchange
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=self.queue_name,
            routing_key=self.routing_key  # Give me order.order.created!
        )

    def start_consuming(self):
        # Tell RabbitMQ: call self.callback when message arrives
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback
        )

        logger.info("🎧 Payment Service is listening for events...")
        self.channel.start_consuming()  # Blocking call - waits forever
```

**When event arrives, callback is invoked:**

```python
def callback(self, ch, method, properties, body):
    event_data = json.loads(body)
    logger.info(f"📥 Received event: {event_data['event_type']}")

    # Process payment
    self.process_payment(event_data)

    # Acknowledge message (tell RabbitMQ: I'm done, remove it from queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

---

### Step 7: Payment Service Processes Payment

**Payment processing** at `payment-service/app/event_consumer.py:66-118`

```python
def process_payment(self, order_data: dict):
    # Create payment record in database
    payment = Payment(
        order_id=order_data['order_id'],
        user_id=order_data['user_id'],
        amount=Decimal(order_data['total_amount']),
        status='pending'
    )
    db.add(payment)
    db.commit()

    # Simulate payment gateway call (1 second delay)
    time.sleep(1)  # User doesn't wait for this! 🎉

    # Update payment status
    payment.status = 'completed'
    payment.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    db.commit()

    # Publish another event!
    self.publish_payment_event(payment, order_data)
```

---

### Step 8: Payment Service → RabbitMQ (Another Event!)

**Payment service publishes PaymentProcessed event:**

```python
def publish_payment_event(self, payment: Payment, order_data: dict):
    event_data = {
        "event_type": "payment.processed",
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "user_id": payment.user_id,
        "user_email": order_data['user_email'],
        "amount": str(payment.amount),
        "status": payment.status,
        "transaction_id": payment.transaction_id
    }

    self.channel.basic_publish(
        exchange=self.exchange_name,
        routing_key="payment.payment.processed",  # New routing key!
        body=json.dumps(event_data, default=str)
    )
```

---

### Step 9: Email Service Receives Event

**Email Service is listening** at `email-service/app/event_consumer.py:30-56`

```python
class EmailEventConsumer:
    def __init__(self):
        self.queue_name = "email_service_queue"
        self.routing_key = "payment.payment.processed"  # I want these!

    def callback(self, ch, method, properties, body):
        event_data = json.loads(body)

        # Send email
        if event_data.get('status') == 'completed':
            self.send_confirmation_email(event_data)

        ch.basic_ack(delivery_tag=method.delivery_tag)
```

---

### Step 10: Email Service Sends Email

**Email sending** at `email-service/app/email_sender.py:18-72`

```python
def send_order_confirmation_email(user_email, order_id, amount, transaction_id):
    # Create email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Order Confirmation - Order #{order_id}"
    msg['To'] = user_email

    # Simulate email delay (2 seconds)
    time.sleep(2)  # User STILL doesn't wait! 🎉

    # Send via SMTP (MailHog)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.send_message(msg)

    logger.info(f"✅ Email sent successfully to {user_email}")
```

---

## Timeline Visualization

```
TIME: 0ms
│ User clicks checkout
│
▼
TIME: 5ms
│ API Gateway receives request
│ Forwards to Order Service (HTTP)
│
▼
TIME: 13ms
│ ✅ Order Service:
│    - Creates order in DB (10ms)
│    - Publishes event to RabbitMQ (3ms)
│    - RETURNS RESPONSE TO USER
│
│ ════════════════════════════════════════════
│ USER GOT RESPONSE! (13ms total)
│ Everything below happens in BACKGROUND
│ ════════════════════════════════════════════
│
▼
TIME: 20ms
│ RabbitMQ routes event to payment_service_queue
│
▼
TIME: 50ms
│ Payment Service receives event from queue
│ Starts processing
│
▼
TIME: 1,050ms (1 second later)
│ ✅ Payment Service:
│    - Payment processed (1s delay)
│    - Publishes PaymentProcessed event
│
▼
TIME: 1,070ms
│ RabbitMQ routes event to email_service_queue
│
▼
TIME: 1,100ms
│ Email Service receives event from queue
│ Starts sending email
│
▼
TIME: 3,100ms (3 seconds from checkout)
│ ✅ Email Service:
│    - Email sent (2s delay)
│    - COMPLETE!
│
TOTAL TIME: ~3 seconds
USER WAITED: 13ms (0.4% of total time!)
```

---

## Communication Patterns Compared

### Pattern 1: Synchronous HTTP (API Gateway → Order Service)

**Code in API Gateway:**
```python
response = await client.post(
    "http://order-service:8001/checkout",
    json=request_data
)
# Waits here until Order Service responds
data = response.json()
return data  # Send to user
```

**Visual:**
```
API Gateway                Order Service
    │                          │
    ├─── POST /checkout ──────>│
    │                          │ (processing...)
    │                          │
    │<──── Response ───────────┤
    │                          │
    ├─ Send to user
```

**Characteristics:**
- ✅ Simple and direct
- ✅ Get immediate response
- ✅ Easy error handling
- ❌ Caller waits for processing
- ❌ Tight coupling (needs to know URL)
- ❌ Caller fails if service is down

---

### Pattern 2: Async Events (Order → Payment → Email)

**Code in Order Service:**
```python
# Create order
order = Order(...)
db.commit()

# Publish event (fire and forget!)
event_publisher.publish_event(
    routing_key="order.order.created",
    event_data={"order_id": order.id, ...}
)

# Return immediately - don't wait for payment!
return order
```

**Visual:**
```
Order Service          RabbitMQ              Payment Service
    │                     │                        │
    ├─ Publish event ────>│                        │
    │                     ├─ Store in queue        │
    │                     │                        │
    │<─ ACK ──────────────┤                        │
    │                     │                        │
Return to user           │                        │
                         │                        │
                         │<─ Pull message ────────┤
                         │                        │
                         ├─ Deliver message ─────>│
                         │                        │ (processing...)
                         │                        │
                         │<─ ACK ─────────────────┤
                         │                        │
                    Delete from queue              │
```

**Characteristics:**
- ✅ Non-blocking (fast response)
- ✅ Loose coupling (services don't know each other)
- ✅ Resilient (retry if service is down)
- ✅ Scalable (multiple consumers)
- ❌ More complex
- ❌ Eventual consistency (not immediate)

---

## Why RabbitMQ?

### Problem Without Message Broker

**Direct HTTP calls everywhere:**
```
Order Service → Payment Service → Email Service
              (HTTP)            (HTTP)
```

**Issues:**
1. **Coupling:** Order Service needs to know Payment Service URL
2. **Blocking:** Order Service waits for Payment Service
3. **Cascading failures:** If Email fails, everything fails
4. **No retry:** Failed request = lost operation

### Solution With RabbitMQ

**Events through message broker:**
```
Order Service → RabbitMQ → Payment Service
                         → Email Service
```

**Benefits:**
1. **Decoupling:** Services only know about events
2. **Non-blocking:** Order Service returns immediately
3. **Resilient:** Failed service = messages wait in queue
4. **Automatic retry:** RabbitMQ redelivers failed messages

---

## RabbitMQ Components Explained

### 1. Exchange

**What:** Routes messages to queues based on rules

**Your exchange:**
```python
exchange_name = "ecommerce_events"
exchange_type = "topic"  # Routes based on pattern matching
```

**Types:**
- **Topic** (what you use): Routes by pattern (order.*, payment.*)
- **Direct**: Exact match only
- **Fanout**: Send to all queues (broadcast)
- **Headers**: Route by message headers

### 2. Queue

**What:** Holds messages for a consumer

**Your queues:**
```python
payment_service_queue  # Holds OrderCreated events
email_service_queue    # Holds PaymentProcessed events
```

**Properties:**
- **Durable:** Survives RabbitMQ restart (you have this)
- **Auto-delete:** Deleted when no consumers
- **Exclusive:** Only one connection allowed

### 3. Binding

**What:** Link between exchange and queue

**Your bindings:**
```python
# Payment Service binding
queue: payment_service_queue
exchange: ecommerce_events
routing_key: order.order.created

# Email Service binding
queue: email_service_queue
exchange: ecommerce_events
routing_key: payment.payment.processed
```

**Meaning:** "Send messages with this routing key to this queue"

### 4. Message

**What:** The actual data being sent

**Your message structure:**
```json
{
  "event_type": "order.created",
  "event_id": "uuid-here",
  "timestamp": "2025-12-21T...",
  "order_id": 1,
  "user_id": 1,
  "user_email": "test@example.com",
  "total_amount": "1299.99",
  "items": [...]
}
```

---

## Message Acknowledgment (ACK)

### Why ACK Matters

**Without ACK:**
```
Service receives message
    ↓
Service crashes while processing
    ↓
Message is LOST! ❌
```

**With ACK:**
```
Service receives message
    ↓
Service processes message
    ↓
Service sends ACK
    ↓
RabbitMQ deletes message ✅

OR

Service crashes before ACK
    ↓
RabbitMQ redelivers message to another instance ✅
```

### Your Code

**Payment Service** at `payment-service/app/event_consumer.py:148-159`

```python
def callback(self, ch, method, properties, body):
    try:
        event_data = json.loads(body)
        self.process_payment(event_data)

        # ACK: "I successfully processed this message"
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error: {e}")

        # NACK: "I failed, don't retry this message"
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

---

## Advanced: Scaling with Events

### One Consumer (Current)

```
Order Service → RabbitMQ → payment_service_queue → Payment Service (1 instance)
                                                    ↓
                                              Processes 1 msg at a time
```

### Multiple Consumers (Scalable!)

```
Order Service → RabbitMQ → payment_service_queue ┬→ Payment Service #1
                                                  ├→ Payment Service #2
                                                  └→ Payment Service #3

Each instance processes messages in parallel!
RabbitMQ distributes messages using round-robin
```

**To scale, just run:**
```bash
docker compose up -d --scale payment-service=3
```

---

## Error Handling

### Scenario: Payment Service Crashes

```
1. Order created, event published to RabbitMQ ✅
2. Payment Service pulls message from queue
3. Payment Service crashes mid-processing ❌
4. Message NOT acknowledged (no ACK sent)
5. RabbitMQ waits timeout period
6. RabbitMQ redelivers message to another instance ✅
7. New instance processes successfully
8. Sends ACK
9. Message deleted from queue ✅
```

**Result: No data loss! Message is retried automatically**

### Scenario: Invalid Message

```python
def callback(self, ch, method, properties, body):
    try:
        event_data = json.loads(body)
        self.process_payment(event_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Failed to process: {e}")

        # Don't requeue (requeue=False)
        # Send to dead-letter queue in production
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

---

## Comparison Table

| Aspect | HTTP Sync | Events (RabbitMQ) |
|--------|-----------|-------------------|
| **Speed** | Waits for response | Fire and forget |
| **Coupling** | Tight (needs URL) | Loose (only knows event) |
| **Failure** | Caller sees error | Retry automatically |
| **Scaling** | Complex | Easy (add consumers) |
| **Debugging** | Simple (direct) | Complex (async) |
| **Use Case** | User needs immediate answer | Background processing |

---

## When to Use Each

### Use HTTP (Synchronous)

✅ User needs immediate response
✅ Simple request-response
✅ Getting data (GET requests)
✅ Low latency required

**Examples:**
- API Gateway → Order Service (create order)
- Frontend → API (get user profile)
- Service → Database query

### Use Events (Asynchronous)

✅ Background processing
✅ Long-running tasks
✅ Multiple services need to react
✅ Resilience important

**Examples:**
- Order → Payment processing
- Payment → Email notification
- User signup → Welcome email + Analytics + Recommendations
- File upload → Virus scan + Thumbnail generation + Storage

---

## Summary

### Your Communication Patterns:

1. **Client → API Gateway → Order Service**
   - HTTP synchronous
   - User gets immediate response
   - Time: 13ms

2. **Order Service → RabbitMQ → Payment Service**
   - Event-driven async
   - OrderCreated event
   - Payment processes in background
   - Time: ~1s (user doesn't wait)

3. **Payment Service → RabbitMQ → Email Service**
   - Event-driven async
   - PaymentProcessed event
   - Email sends in background
   - Time: ~2s (user doesn't wait)

**Total user wait: 13ms**
**Total processing: ~3s**
**User experience: 583x better than monolith! 🚀**
