# Event-Driven Architecture

## Overview

Event-Driven Architecture (EDA) is a software design pattern where the flow of the program is determined by events: significant changes in state that are communicated asynchronously between loosely coupled components.

**Core Concept:** Systems react to events rather than making direct calls to each other.

**Key Characteristics:**
- Asynchronous communication
- Loose coupling between components
- Event producers don't know about consumers
- Real-time or near-real-time processing
- Natural fit for distributed systems

This document covers the essential patterns and concepts of event-driven architecture, including Event Sourcing, CQRS, Event Streaming vs Messaging, and the Saga pattern.

---

## 1. Event Sourcing

### What is Event Sourcing?

**Definition:** Instead of storing just the current state, store the sequence of events that led to that state.

**Key Insight:** The event log becomes the source of truth, not the database state.

### Traditional State-Based Approach

```
Bank Account Example:

State-Based Storage:
+----------+----------+
| account  | balance  |
+----------+----------+
| 12345    | $1,000   |
+----------+----------+

Operations:
1. Deposit $500  → UPDATE accounts SET balance = 1500 WHERE account = 12345
2. Withdraw $200 → UPDATE accounts SET balance = 1300 WHERE account = 12345

Current State:
+----------+----------+
| account  | balance  |
+----------+----------+
| 12345    | $1,300   |
+----------+----------+

Lost Information:
├── How did we get to $1,300?
├── When did transactions occur?
├── Who made the transactions?
└── Cannot replay history
```

### Event Sourcing Approach

```
Event Store:
+----+----------+---------+---------+----------+-----------+
| ID | account  | event   | amount  | when     | who       |
+----+----------+---------+---------+----------+-----------+
| 1  | 12345    | CREATED | $1,000  | 10:00 AM | system    |
| 2  | 12345    | DEPOSIT | $500    | 10:30 AM | alice     |
| 3  | 12345    | WITHDRAWAL | $200 | 11:00 AM | alice     |
+----+----------+---------+---------+----------+-----------+

Current State (computed from events):
balance = CREATED($1,000) + DEPOSIT($500) - WITHDRAWAL($200) = $1,300

Benefits:
├── Complete audit trail
├── Can reconstruct state at any point in time
├── Can replay events
├── Can add new projections without losing data
└── Debugging is easier (see what happened)
```

### Event Sourcing Implementation

**Example: Order System**
```python
# Event definitions
class OrderEvent:
    def __init__(self, order_id, timestamp):
        self.order_id = order_id
        self.timestamp = timestamp

class OrderCreated(OrderEvent):
    def __init__(self, order_id, user_id, items):
        super().__init__(order_id, datetime.now())
        self.user_id = user_id
        self.items = items

class OrderShipped(OrderEvent):
    def __init__(self, order_id, tracking_number):
        super().__init__(order_id, datetime.now())
        self.tracking_number = tracking_number

class OrderCancelled(OrderEvent):
    def __init__(self, order_id, reason):
        super().__init__(order_id, datetime.now())
        self.reason = reason

# Event store
class EventStore:
    def __init__(self):
        self.events = []  # In production: database or event stream

    def append(self, event):
        self.events.append(event)

    def get_events(self, order_id):
        return [e for e in self.events if e.order_id == order_id]

# Order aggregate (rebuilds state from events)
class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self.user_id = None
        self.items = []
        self.status = None
        self.tracking_number = None

    def apply_event(self, event):
        """Rebuild state from event"""
        if isinstance(event, OrderCreated):
            self.user_id = event.user_id
            self.items = event.items
            self.status = 'CREATED'
        elif isinstance(event, OrderShipped):
            self.status = 'SHIPPED'
            self.tracking_number = event.tracking_number
        elif isinstance(event, OrderCancelled):
            self.status = 'CANCELLED'

    @staticmethod
    def load(order_id, event_store):
        """Reconstitute order from events"""
        order = Order(order_id)
        events = event_store.get_events(order_id)

        for event in events:
            order.apply_event(event)

        return order

# Usage
event_store = EventStore()

# Create order
order_id = 'ORD-001'
event_store.append(OrderCreated(order_id, user_id=123, items=['product1', 'product2']))
event_store.append(OrderShipped(order_id, tracking_number='TRACK-123'))

# Load order (rebuilds state from events)
order = Order.load(order_id, event_store)
print(f"Order status: {order.status}")  # SHIPPED
print(f"Tracking: {order.tracking_number}")  # TRACK-123

# Can replay events to see order history
events = event_store.get_events(order_id)
for event in events:
    print(f"{event.timestamp}: {event.__class__.__name__}")

# Output:
# 2024-01-15 10:00:00: OrderCreated
# 2024-01-15 11:30:00: OrderShipped
```

### Event Sourcing Patterns

#### Snapshots

**Problem:** Replaying thousands of events is slow.

**Solution:** Periodically save snapshots of state.

```python
class OrderSnapshot:
    def __init__(self, order_id, version, state):
        self.order_id = order_id
        self.version = version  # Event number when snapshot taken
        self.state = state
        self.timestamp = datetime.now()

class EventStore:
    def __init__(self):
        self.events = []
        self.snapshots = {}

    def save_snapshot(self, order_id, version, state):
        self.snapshots[order_id] = OrderSnapshot(order_id, version, state)

    def load_with_snapshot(self, order_id):
        # Load latest snapshot
        snapshot = self.snapshots.get(order_id)

        if snapshot:
            order = snapshot.state
            # Only replay events after snapshot
            events = [e for e in self.events
                     if e.order_id == order_id and e.version > snapshot.version]
        else:
            order = Order(order_id)
            events = [e for e in self.events if e.order_id == order_id]

        for event in events:
            order.apply_event(event)

        return order

# Every 100 events, save snapshot
if event_count % 100 == 0:
    event_store.save_snapshot(order_id, event_count, order)
```

### Benefits of Event Sourcing

```
✓ Complete Audit Trail
  ├── Every change recorded
  ├── Who, what, when
  └── Regulatory compliance

✓ Temporal Queries
  ├── "What was the account balance yesterday?"
  ├── "When did the order status change?"
  └── Replay to any point in time

✓ Event Replay
  ├── Fix bugs by replaying events with corrected logic
  ├── Add new features using historical data
  └── Testing with real event sequences

✓ Multiple Projections
  ├── Same events → Different read models
  ├── Add projections without losing data
  └── Optimize for different query patterns
```

### Challenges of Event Sourcing

```
✗ Complexity
  ├── More complex than CRUD
  ├── Learning curve for developers
  └── Need event versioning strategy

✗ Event Schema Evolution
  ├── Events are immutable
  ├── Cannot change past events
  └── Need versioning and upcasting

✗ Querying Difficulty
  ├── Cannot directly query current state
  ├── Must replay events or use projections
  └── Eventual consistency

✗ Event Store Scaling
  ├── Events accumulate over time
  ├── Storage grows continuously
  └── Need archival strategy
```

### When to Use Event Sourcing

```
Good fit:
✓ Audit requirements (finance, healthcare)
✓ Complex business processes
✓ Temporal queries needed
✓ Event replay valuable
✓ Multiple projections needed

Not a good fit:
✗ Simple CRUD applications
✗ No audit requirements
✗ Team unfamiliar with pattern
✗ Immediate consistency required
✗ Event volume very high without business value
```

---

## 2. CQRS (Command Query Responsibility Segregation)

### What is CQRS?

**Definition:** Separate the write model (commands) from the read model (queries).

**Key Insight:** Reading and writing have different requirements; optimize each separately.

### Traditional Unified Model

```
Single Model for Read and Write:

            [Application]
                 |
            [Domain Model]
           /             \
      [Database]    [Database]
       (write)       (read)

Same model handles:
├── Complex writes (orders, payments)
├── Simple reads (view order list)
├── Complex reads (analytics, reports)
└── Compromises on both sides
```

### CQRS Approach

```
Separate Models:

Commands (Writes):              Queries (Reads):
[Create Order Command]          [Get Orders Query]
        |                               |
[Write Model]                   [Read Model 1] (order list)
        |                       [Read Model 2] (analytics)
[Write Database]                [Read Model 3] (reports)
        |                               |
        +-------[Events]----------------+
             (synchronization)

Benefits:
├── Write model optimized for transactions
├── Read models optimized for specific queries
├── Can have multiple read models
└── Scale reads and writes independently
```

### CQRS Implementation

**Example: E-commerce Order System**

```python
# Commands (Write Side)
class CreateOrderCommand:
    def __init__(self, user_id, items):
        self.user_id = user_id
        self.items = items

class CancelOrderCommand:
    def __init__(self, order_id, reason):
        self.order_id = order_id
        self.reason = reason

# Command Handlers (Write Model)
class OrderCommandHandler:
    def __init__(self, event_store, event_bus):
        self.event_store = event_store
        self.event_bus = event_bus

    def handle_create_order(self, command):
        # Validate
        if not command.items:
            raise ValueError("Order must have items")

        # Generate ID
        order_id = generate_uuid()

        # Create event
        event = OrderCreated(order_id, command.user_id, command.items)

        # Store event
        self.event_store.append(event)

        # Publish event for read model updates
        self.event_bus.publish(event)

        return order_id

    def handle_cancel_order(self, command):
        # Load order from events
        order = Order.load(command.order_id, self.event_store)

        # Validate
        if order.status == 'SHIPPED':
            raise ValueError("Cannot cancel shipped order")

        # Create event
        event = OrderCancelled(command.order_id, command.reason)

        # Store and publish
        self.event_store.append(event)
        self.event_bus.publish(event)

# Queries (Read Side)
class GetOrdersQuery:
    def __init__(self, user_id, page=1, limit=20):
        self.user_id = user_id
        self.page = page
        self.limit = limit

class GetOrderDetailsQuery:
    def __init__(self, order_id):
        self.order_id = order_id

# Read Models (Optimized for Queries)
class OrderListReadModel:
    """Optimized for displaying order lists"""
    def __init__(self, database):
        self.db = database

    def update(self, event):
        """Update read model when events occur"""
        if isinstance(event, OrderCreated):
            self.db.execute("""
                INSERT INTO order_list (order_id, user_id, created_at, status)
                VALUES (:order_id, :user_id, :timestamp, 'CREATED')
            """, {
                'order_id': event.order_id,
                'user_id': event.user_id,
                'timestamp': event.timestamp
            })
        elif isinstance(event, OrderShipped):
            self.db.execute("""
                UPDATE order_list
                SET status = 'SHIPPED', shipped_at = :timestamp
                WHERE order_id = :order_id
            """, {
                'order_id': event.order_id,
                'timestamp': event.timestamp
            })

    def get_user_orders(self, user_id, page, limit):
        """Fast query from denormalized table"""
        return self.db.query("""
            SELECT order_id, created_at, status
            FROM order_list
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """, {
            'user_id': user_id,
            'limit': limit,
            'offset': (page - 1) * limit
        })

class OrderAnalyticsReadModel:
    """Optimized for analytics and reporting"""
    def __init__(self, database):
        self.db = database

    def update(self, event):
        if isinstance(event, OrderCreated):
            # Update daily statistics
            self.db.execute("""
                INSERT INTO daily_order_stats (date, order_count, total_value)
                VALUES (:date, 1, :value)
                ON CONFLICT (date) DO UPDATE
                SET order_count = daily_order_stats.order_count + 1,
                    total_value = daily_order_stats.total_value + :value
            """, {
                'date': event.timestamp.date(),
                'value': calculate_order_value(event.items)
            })

    def get_daily_stats(self, start_date, end_date):
        return self.db.query("""
            SELECT date, order_count, total_value
            FROM daily_order_stats
            WHERE date BETWEEN :start AND :end
            ORDER BY date
        """, {'start': start_date, 'end': end_date})

# Query Handlers (Read Model)
class OrderQueryHandler:
    def __init__(self, read_model):
        self.read_model = read_model

    def handle_get_orders(self, query):
        return self.read_model.get_user_orders(
            query.user_id,
            query.page,
            query.limit
        )

# Event Bus (connects write and read sides)
class EventBus:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, handler):
        self.subscribers.append(handler)

    def publish(self, event):
        for subscriber in self.subscribers:
            subscriber.update(event)

# Wiring it together
event_store = EventStore()
event_bus = EventBus()

# Subscribe read models to events
order_list_model = OrderListReadModel(database)
analytics_model = OrderAnalyticsReadModel(analytics_db)

event_bus.subscribe(order_list_model)
event_bus.subscribe(analytics_model)

# Command handler publishes to event bus
command_handler = OrderCommandHandler(event_store, event_bus)

# Usage
# Write: Create order
command = CreateOrderCommand(user_id=123, items=['product1', 'product2'])
order_id = command_handler.handle_create_order(command)

# Events automatically update read models via event bus

# Read: Query orders
query = GetOrdersQuery(user_id=123, page=1, limit=10)
orders = query_handler.handle_get_orders(query)
```

### CQRS Benefits

```
✓ Independent Scaling
  ├── Scale read and write databases separately
  ├── Read-heavy: Add read replicas
  └── Write-heavy: Optimize write database

✓ Optimized Data Models
  ├── Write model: Normalized, transactional
  ├── Read model: Denormalized, query-optimized
  └── Multiple read models for different use cases

✓ Simplified Queries
  ├── No complex joins
  ├── Pre-computed aggregations
  └── Fast reads

✓ Technology Choice
  ├── Write: PostgreSQL (ACID)
  ├── Read: Elasticsearch (search)
  └── Read: Redis (caching)
```

### CQRS Challenges

```
✗ Eventual Consistency
  ├── Read models lag behind writes
  ├── User creates order, doesn't see it immediately
  └── Need to handle in UI

✗ Increased Complexity
  ├── Two models instead of one
  ├── Synchronization logic
  └── More moving parts

✗ Duplicate Code
  ├── Same data in multiple models
  ├── Update logic in multiple places
  └── Maintenance overhead
```

### CQRS Without Event Sourcing

CQRS doesn't require event sourcing:

```
Simplified CQRS:

Commands → Write Model → Database (PostgreSQL)
                              |
                         [Trigger/CDC]
                              |
Queries ← Read Model ← Materialized View

Benefits:
├── Simpler than full event sourcing
├── Still separates read/write concerns
├── Can use database features (triggers, views)
└── Lower complexity
```

---

## 3. Event Streaming vs Messaging

Both enable event-driven architecture but with different characteristics.

### Messaging (Message Queues)

**Characteristics:**
- Point-to-point or pub/sub
- Messages deleted after consumption
- Focuses on command delivery
- Examples: RabbitMQ, AWS SQS, ActiveMQ

**Message Queue Pattern:**
```
Producer → Queue → Consumer

Order Service → [Order Processing Queue] → Fulfillment Service

Message lifecycle:
1. Producer sends message
2. Queue stores message
3. Consumer receives message
4. Consumer acknowledges
5. Queue deletes message (gone forever)
```

**Pub/Sub Pattern:**
```
Publisher → Topic → Subscribers

Order Service → [Order Events Topic] ─┬→ Email Service
                                      ├→ Analytics Service
                                      └→ Inventory Service

Each subscriber gets copy, then message deleted from their subscription
```

**Example: RabbitMQ**
```python
import pika

# Producer
connection = pika.BlockingConnection()
channel = connection.channel()
channel.queue_declare(queue='orders')

channel.basic_publish(
    exchange='',
    routing_key='orders',
    body=json.dumps({'order_id': '123', 'status': 'created'})
)

# Consumer
def callback(ch, method, properties, body):
    order = json.loads(body)
    process_order(order)
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Message deleted

channel.basic_consume(queue='orders', on_message_callback=callback)
channel.start_consuming()

# Message is deleted after processing
# Cannot replay history
```

### Event Streaming

**Characteristics:**
- Append-only log
- Events retained (configurable duration)
- Consumers track their own position
- Can replay events
- Examples: Apache Kafka, AWS Kinesis, Pulsar

**Event Stream Pattern:**
```
Producer → Stream → Consumers

Order Service → [Order Event Stream]
                      ↓
                  [Offset 0] OrderCreated
                  [Offset 1] OrderPaid
                  [Offset 2] OrderShipped
                  [Offset 3] OrderDelivered
                      ↓
                  Consumer A (at offset 2)
                  Consumer B (at offset 3)
                  Consumer C (at offset 0 - replaying from start)

Events never deleted (or retained for days/months)
Each consumer tracks its own position
```

**Example: Apache Kafka**
```python
from kafka import KafkaProducer, KafkaConsumer

# Producer
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Produce events (retained in stream)
producer.send('order-events', {'event': 'OrderCreated', 'order_id': '123'})
producer.send('order-events', {'event': 'OrderPaid', 'order_id': '123'})
producer.send('order-events', {'event': 'OrderShipped', 'order_id': '123'})

# Consumer 1: Real-time processing (reads new events)
consumer1 = KafkaConsumer(
    'order-events',
    bootstrap_servers=['kafka:9092'],
    group_id='email-service',
    auto_offset_reset='latest'  # Start from latest
)

for message in consumer1:
    event = message.value
    send_email_for_event(event)

# Consumer 2: Batch analytics (replay all history)
consumer2 = KafkaConsumer(
    'order-events',
    bootstrap_servers=['kafka:9092'],
    group_id='analytics',
    auto_offset_reset='earliest'  # Start from beginning
)

for message in consumer2:
    event = message.value
    analyze_event(event)

# Consumer 3: Debugging (replay from specific time)
consumer3 = KafkaConsumer(
    'order-events',
    bootstrap_servers=['kafka:9092'],
    group_id='debug-service'
)

# Seek to timestamp (e.g., 1 hour ago)
from kafka import TopicPartition
tp = TopicPartition('order-events', 0)
consumer3.assign([tp])
consumer3.seek(tp, timestamp_ms=time.time() * 1000 - 3600000)

# Events still available for replay!
```

### Comparison

```
                Messaging (RabbitMQ)       Event Streaming (Kafka)
─────────────────────────────────────────────────────────────────────
Message           Deleted after consumed      Retained (days/months)
Retention

Replay            Not possible                Can replay from any point
Capability

Consumer          Push (broker sends)         Pull (consumer fetches)
Model

Ordering          Queue-level ordering        Partition-level ordering
Guarantee

Scalability       Moderate                    Very high (partitioning)

Typical           Task queues, RPC            Event sourcing, streaming
Use Cases         Command processing          Analytics, CDC

Examples          RabbitMQ, SQS, ActiveMQ     Kafka, Kinesis, Pulsar

Best For          Work distribution           Event history, replay
                  Command/reply               Stream processing
```

### When to Use Each

**Use Messaging (RabbitMQ, SQS) when:**
```
✓ Task distribution (work queues)
✓ Fire-and-forget commands
✓ Don't need message history
✓ Simple pub/sub patterns
✓ Lower throughput requirements

Examples:
├── Send email
├── Process image upload
├── Execute background job
└── One-time notifications
```

**Use Event Streaming (Kafka) when:**
```
✓ Need event history
✓ Multiple consumers need same events
✓ Replay capability required
✓ High throughput (millions of events/sec)
✓ Event sourcing
✓ Stream processing (real-time analytics)

Examples:
├── Order events (need audit trail)
├── User activity tracking
├── IoT sensor data
├── Change data capture (CDC)
└── Real-time analytics
```

---

## 4. Saga Pattern (Distributed Transactions)

### The Problem: Distributed Transactions

```
Order Creation Spans Multiple Services:

1. Order Service: Create order
2. Payment Service: Charge payment
3. Inventory Service: Reserve items
4. Shipping Service: Schedule shipment

Traditional ACID transaction:
BEGIN TRANSACTION
  INSERT INTO orders ...
  UPDATE payments ...
  UPDATE inventory ...
  UPDATE shipping ...
COMMIT

Problem in Microservices:
├── Services have separate databases
├── Cannot use single transaction
├── What if payment succeeds but inventory fails?
└── Need distributed coordination
```

### What is the Saga Pattern?

**Definition:** A sequence of local transactions where each service updates its own database and publishes an event/message to trigger the next step. If any step fails, execute compensating transactions to undo previous steps.

**Key Concepts:**
- Break distributed transaction into local transactions
- Each service commits its local transaction
- Coordination via events or orchestration
- Compensating transactions for rollback

### Saga Implementations

#### 1. Choreography-Based Saga

**Definition:** Services communicate via events; no central coordinator.

**Example: Order Processing**
```
Happy Path (all succeed):

1. Order Service:
   ├── Create order (status=PENDING)
   ├── Publish OrderCreated event
   └── Commit local transaction

2. Payment Service (listens to OrderCreated):
   ├── Charge customer
   ├── Publish PaymentCompleted event
   └── Commit local transaction

3. Inventory Service (listens to PaymentCompleted):
   ├── Reserve items
   ├── Publish InventoryReserved event
   └── Commit local transaction

4. Shipping Service (listens to InventoryReserved):
   ├── Schedule shipment
   ├── Publish ShipmentScheduled event
   └── Commit local transaction

5. Order Service (listens to ShipmentScheduled):
   ├── Update order status = CONFIRMED
   └── Commit local transaction

Result: Order successfully processed
```

**Failure Path (with compensating transactions):**
```
Failure Scenario: Inventory reservation fails

1. Order Service:
   ├── Create order (PENDING)
   └── Publish OrderCreated ✓

2. Payment Service:
   ├── Charge customer ($100)
   └── Publish PaymentCompleted ✓

3. Inventory Service:
   ├── Try to reserve items
   ├── FAILS (out of stock)
   └── Publish InventoryReservationFailed ✗

4. Payment Service (listens to InventoryReservationFailed):
   ├── Compensate: Refund customer ($100)
   └── Publish PaymentRefunded

5. Order Service (listens to PaymentRefunded):
   ├── Update order status = CANCELLED
   └── Publish OrderCancelled

Result: Order cancelled, customer refunded (consistent state)
```

**Implementation:**
```python
# Order Service
class OrderService:
    def create_order(self, user_id, items):
        # Local transaction
        order = db.orders.create({
            'user_id': user_id,
            'items': items,
            'status': 'PENDING'
        })
        db.commit()

        # Publish event
        event_bus.publish(OrderCreated(order.id, user_id, items))

        return order

    def on_shipment_scheduled(self, event):
        # Update order when saga completes
        order = db.orders.get(event.order_id)
        order.status = 'CONFIRMED'
        db.commit()

    def on_payment_refunded(self, event):
        # Compensate: cancel order
        order = db.orders.get(event.order_id)
        order.status = 'CANCELLED'
        db.commit()

# Payment Service
class PaymentService:
    def on_order_created(self, event):
        try:
            # Local transaction
            payment = db.payments.create({
                'order_id': event.order_id,
                'amount': calculate_total(event.items),
                'status': 'COMPLETED'
            })
            db.commit()

            # Next step
            event_bus.publish(PaymentCompleted(event.order_id, payment.id))
        except PaymentError as e:
            # Publish failure event
            event_bus.publish(PaymentFailed(event.order_id, str(e)))

    def on_inventory_reservation_failed(self, event):
        # Compensating transaction
        payment = db.payments.get_by_order(event.order_id)
        refund = db.refunds.create({
            'payment_id': payment.id,
            'amount': payment.amount
        })
        db.commit()

        # Notify previous services
        event_bus.publish(PaymentRefunded(event.order_id))

# Inventory Service
class InventoryService:
    def on_payment_completed(self, event):
        try:
            # Local transaction
            for item in event.items:
                db.inventory.decrement(item.id, item.quantity)
            db.commit()

            event_bus.publish(InventoryReserved(event.order_id))
        except OutOfStockError:
            # Cannot compensate previous steps directly
            # Publish failure event so they can compensate
            event_bus.publish(InventoryReservationFailed(event.order_id))
```

**Choreography Benefits:**
```
✓ Loose coupling (services don't know about each other)
✓ Simple for small sagas (2-3 services)
✓ No single point of failure
✓ Natural event-driven architecture
```

**Choreography Challenges:**
```
✗ Difficult to understand flow (no central definition)
✗ Hard to add new steps
✗ Circular dependencies between events
✗ Difficult to monitor (distributed state)
```

#### 2. Orchestration-Based Saga

**Definition:** Central orchestrator directs the saga flow.

**Example: Order Processing**
```
Order Saga Orchestrator:

Step 1: Create Order → Order Service
Step 2: Charge Payment → Payment Service
Step 3: Reserve Inventory → Inventory Service
Step 4: Schedule Shipment → Shipping Service

Orchestrator knows:
├── Sequence of steps
├── Compensation for each step
└── Current state of saga
```

**Implementation:**
```python
class OrderSagaOrchestrator:
    def __init__(self):
        self.steps = [
            CreateOrderStep(),
            ChargePaymentStep(),
            ReserveInventoryStep(),
            ScheduleShipmentStep()
        ]

    async def execute(self, saga_data):
        """Execute saga steps"""
        completed_steps = []

        try:
            for step in self.steps:
                # Execute step
                await step.execute(saga_data)
                completed_steps.append(step)

            # All steps succeeded
            return SagaSuccess(saga_data)

        except SagaStepFailed as e:
            # Failure: compensate in reverse order
            for step in reversed(completed_steps):
                await step.compensate(saga_data)

            return SagaFailed(saga_data, e)

# Step definitions
class CreateOrderStep:
    async def execute(self, saga_data):
        response = await http.post('http://order-service/orders', {
            'user_id': saga_data.user_id,
            'items': saga_data.items
        })

        if response.status != 201:
            raise SagaStepFailed('Order creation failed')

        saga_data.order_id = response.json()['order_id']

    async def compensate(self, saga_data):
        # Undo: delete order
        await http.delete(f'http://order-service/orders/{saga_data.order_id}')

class ChargePaymentStep:
    async def execute(self, saga_data):
        response = await http.post('http://payment-service/charge', {
            'order_id': saga_data.order_id,
            'amount': saga_data.total
        })

        if response.status != 200:
            raise SagaStepFailed('Payment failed')

        saga_data.payment_id = response.json()['payment_id']

    async def compensate(self, saga_data):
        # Undo: refund payment
        await http.post(f'http://payment-service/refund', {
            'payment_id': saga_data.payment_id
        })

class ReserveInventoryStep:
    async def execute(self, saga_data):
        response = await http.post('http://inventory-service/reserve', {
            'order_id': saga_data.order_id,
            'items': saga_data.items
        })

        if response.status != 200:
            raise SagaStepFailed('Inventory reservation failed')

    async def compensate(self, saga_data):
        # Undo: release inventory
        await http.post('http://inventory-service/release', {
            'order_id': saga_data.order_id
        })

# Usage
saga_data = SagaData(user_id=123, items=[...], total=99.99)
orchestrator = OrderSagaOrchestrator()
result = await orchestrator.execute(saga_data)

if isinstance(result, SagaSuccess):
    print("Order completed successfully")
else:
    print(f"Order failed: {result.error}")
    # All steps compensated automatically
```

**Orchestration Benefits:**
```
✓ Clear saga flow definition (easy to understand)
✓ Centralized monitoring and logging
✓ Easy to add/modify steps
✓ Explicit compensation logic
✓ Better for complex sagas (many steps)
```

**Orchestration Challenges:**
```
✗ Orchestrator is single point of failure
✗ Additional service to maintain
✗ Potential bottleneck
✗ More coupling between services
```

### Saga Design Considerations

#### Idempotency

**Problem:** Steps may be retried; must handle duplicates.

```python
class PaymentService:
    def charge_payment(self, order_id, amount, idempotency_key):
        # Check if already processed
        existing = db.payments.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing  # Already processed, return same result

        # Process payment
        payment = stripe.charge(amount)
        db.payments.create({
            'order_id': order_id,
            'amount': amount,
            'idempotency_key': idempotency_key,
            'stripe_id': payment.id
        })
        db.commit()

        return payment

# Caller includes idempotency key
charge_payment(order_id='123', amount=99.99, idempotency_key='order-123-payment')
# If retried, returns same payment object without charging twice
```

#### Compensation Complexity

**Not all operations are easily compensated:**
```
Easy to compensate:
✓ Database writes (delete, update)
✓ Inventory reservation (release)
✓ Payment charge (refund)

Hard to compensate:
✗ Email sent (cannot unsend)
✗ SMS sent (cannot unsend)
✗ Third-party API called (may not support undo)
✗ Physical action triggered (shipped package)

Strategy:
├── Semantic compensation: Send "cancellation" email
├── Flag as compensated: Mark record as void but keep for audit
└── Manual intervention: Alert ops team for manual handling
```

#### Timeout Handling

```python
class SagaStep:
    async def execute_with_timeout(self, saga_data, timeout_seconds=30):
        try:
            return await asyncio.wait_for(
                self.execute(saga_data),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            # Timeout: assume failure, compensate
            raise SagaStepFailed('Step timed out')
```

### Saga vs Traditional Transactions

```
Traditional ACID Transaction:
├── All-or-nothing atomicity
├── Strong consistency
├── Locks held during transaction
├── Simple to reason about
└── Only works within single database

Saga Pattern:
├── Eventually consistent
├── No locks (higher concurrency)
├── More complex logic
├── Works across services/databases
└── Requires compensating transactions

When to use Saga:
✓ Microservices with separate databases
✓ Long-running business processes
✓ Cannot use 2PC (two-phase commit)

When to use Traditional Transaction:
✓ Single database
✓ Strong consistency required
✓ Short-lived operations
```

---

## Summary

### Key Takeaways

**Event Sourcing:**
- Store events, not state
- Complete audit trail
- Temporal queries
- Good for: Audit requirements, event replay, multiple projections

**CQRS:**
- Separate read and write models
- Optimize each independently
- Multiple read models possible
- Good for: Complex reads, different query patterns, scale read/write separately

**Event Streaming vs Messaging:**
- Messaging: Fire-and-forget, messages deleted
- Streaming: Event log, retained, can replay
- Use messaging for: Task queues
- Use streaming for: Event history, analytics

**Saga Pattern:**
- Distributed transactions via local transactions + events
- Choreography: Event-driven, decentralized
- Orchestration: Central coordinator
- Compensating transactions for rollback
- Good for: Cross-service workflows, long-running processes

### Combining Patterns

**Real-World E-commerce Architecture:**
```
Order Service:
├── Event Sourcing (order history)
├── CQRS (optimize for different queries)
├── Event Streaming (Kafka for events)
└── Saga (order processing workflow)

Flow:
1. Command: CreateOrder
2. Event Sourcing: Store OrderCreated event
3. CQRS: Update read models (order list, analytics)
4. Saga: Orchestrate payment, inventory, shipping
5. Event Streaming: All events in Kafka for replay/analytics

Patterns work together:
├── Event Sourcing provides events
├── CQRS consumes events to build read models
├── Saga coordinates distributed workflow
└── Event Streaming ensures reliable delivery
```

---

## Further Reading

**Books:**
- "Domain-Driven Design" by Eric Evans
- "Implementing Domain-Driven Design" by Vaughn Vernon
- "Designing Event-Driven Systems" by Ben Stopford
- "Enterprise Integration Patterns" by Gregor Hohpe

**Online Resources:**
- Event Sourcing by Martin Fowler
- CQRS Journey (Microsoft patterns & practices)
- Apache Kafka documentation
- Microservices.io (Saga pattern)

**Next Topics:**
- Stream processing (Kafka Streams, Apache Flink)
- Data consistency patterns
- Testing event-driven systems
- Monitoring and observability

---

**Remember:** Event-driven architecture introduces complexity. Start simple (messaging), add patterns as needed (event sourcing, CQRS, sagas). Not every service needs event sourcing. Choose patterns that solve real problems, not because they're trendy.
