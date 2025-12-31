# Microservices Architecture

## Overview

Microservices architecture is an approach to building distributed systems where an application is composed of small, independent services that communicate over well-defined APIs. Each service is self-contained, focused on a specific business capability, and can be developed, deployed, and scaled independently.

**Key Characteristics:**
- Services organized around business capabilities
- Independently deployable units
- Decentralized data management
- Infrastructure automation
- Design for failure
- Evolutionary design

This document covers the essential aspects of microservices architecture, helping you understand when and how to apply this pattern effectively.

---

## 1. Service Boundaries and Sizing

### What are Service Boundaries?

**Definition:** The logical separation between different services, determining what functionality belongs to which service.

**Key Principle:** Each service should represent a complete business capability with clear ownership.

### Finding the Right Boundaries

#### Domain-Driven Design (DDD) Approach

**Bounded Context:** A boundary within which a domain model is consistent and has specific meaning.

```
E-commerce Domain:

Catalog Context:
├── Product (id, name, description, images)
├── Category (id, name, hierarchy)
└── Search (indexing, filtering, ranking)

Order Context:
├── Order (id, status, items, total)
├── LineItem (product_id, quantity, price)
└── OrderState (draft, confirmed, shipped, delivered)

Payment Context:
├── Payment (id, amount, status, method)
├── Transaction (id, gateway_response, timestamp)
└── Refund (id, original_payment, amount)

Key Insight: "Product" in Catalog ≠ "Product" in Order
├── Catalog Product: Rich details, images, descriptions
├── Order Product: Snapshot at purchase time (price, name)
└── Different models for different contexts
```

**Example: User Service Boundary**
```
What belongs in User Service:
✓ User registration
✓ Authentication credentials
✓ Profile information
✓ User preferences
✓ Password management

What does NOT belong:
✗ Order history (Order Service)
✗ Payment methods (Payment Service)
✗ Product favorites (Catalog Service)
✗ Shipping addresses (Shipping Service)

Why separate? Different change frequencies, scaling needs, teams
```

#### Business Capability Mapping

**Identify core capabilities:**
```
E-commerce Business Capabilities:

Customer Management:
└── User Service

Product Management:
├── Catalog Service
└── Inventory Service

Order Management:
├── Cart Service
├── Order Service
└── Order Tracking Service

Payment Processing:
├── Payment Service
└── Invoice Service

Fulfillment:
├── Shipping Service
└── Warehouse Service

Customer Support:
├── Notification Service
└── Review Service

Each capability → Potential service boundary
```

### Service Sizing: How Small is "Micro"?

**The Two-Pizza Team Rule (Amazon):**
```
If you can't feed the team with two pizzas, it's too large

Translated:
├── Team size: 5-10 people
├── Service ownership: 1 team owns multiple services
└── Service size: Small enough for one team to understand completely
```

#### Sizing Spectrum

```
[Nanoservices] ← → [Microservices] ← → [Miniservices] ← → [Monolith]
      ↓                    ↓                  ↓                ↓
   Too small          Sweet spot          Acceptable        Too large
   (overhead)         (balanced)         (manageable)     (unwieldy)
```

**Nanoservice (Too Small):**
```
UserPasswordHasher Service:
└── hashPassword(password) → hash

Problem:
├── Too granular
├── Network overhead > business value
├── Difficult to maintain
└── Distributed monolith

Better: Part of User Service
```

**Right-Sized Microservice:**
```
User Service:
├── register(username, email, password)
├── authenticate(username, password)
├── updateProfile(userId, profileData)
├── changePassword(userId, oldPassword, newPassword)
├── resetPassword(email)
└── getUser(userId)

Sweet spot:
├── Cohesive functionality
├── 1-2 developers can maintain
├── ~1000-5000 lines of code
├── Clear business purpose
└── Independent deployment
```

**Miniservice (Still Acceptable):**
```
Order Processing Service:
├── Order creation
├── Order validation
├── Payment coordination
├── Inventory reservation
├── Order tracking
├── Order cancellation
└── Refund processing

Characteristics:
├── More comprehensive
├── ~10,000-20,000 lines of code
├── Small team (3-5 people)
├── Could be split but works as one
└── Single database
```

### Indicators You Got the Boundaries Wrong

#### Too Small (Over-Fragmentation)

**Symptoms:**
```
Problem indicators:
├── Services that always deploy together
├── Changes require modifying 5+ services
├── More network calls than business logic
├── Shared database tables across services
└── Services with < 100 lines of code

Example:
UserService → PasswordService → EmailService → ValidationService
All change together, should be one service
```

#### Too Large (Mini-Monolith)

**Symptoms:**
```
Problem indicators:
├── Service has > 10 distinct responsibilities
├── Team members specialize in "parts" of service
├── Deployment takes > 15 minutes
├── Database has > 50 tables
├── Multiple teams need to coordinate changes
└── Different scaling needs within same service

Example:
EcommerceService handles:
├── Users
├── Products
├── Orders
├── Payments
├── Shipping
└── Reviews

Should be split into separate services
```

### Real-World Example: Amazon's Evolution

**Early Amazon (~2000):**
```
Monolithic Application:
└── All e-commerce functionality in one codebase

Problems:
├── Deployment took hours
├── Scaling was all-or-nothing
├── Teams blocked each other
└── Innovation slowed
```

**Modern Amazon (~2020):**
```
Hundreds of Microservices:

Product Catalog:
├── Product Information Service
├── Image Service
├── Search Service
└── Recommendation Service

Shopping:
├── Cart Service
├── Wishlist Service
├── Price Service
└── Availability Service

Checkout:
├── Order Service
├── Payment Service
├── Tax Service
└── Shipping Service

Each service:
├── Owned by 2-pizza team
├── Deployed independently
├── Scaled independently
└── Uses best-fit technology
```

---

## 2. Communication Patterns

Microservices must communicate with each other. The choice between synchronous and asynchronous communication significantly impacts system behavior.

### Synchronous Communication

**Definition:** Client waits for response before continuing (blocking).

#### HTTP/REST

**Most common pattern:**
```
Order Service needs user info:

Order Service ──HTTP GET /users/123──→ User Service
Order Service ←────{user data}─────────── User Service

Timeline:
├── 0ms: Order Service sends request
├── 5ms: User Service receives request
├── 10ms: User Service queries database
├── 15ms: User Service sends response
├── 20ms: Order Service receives response
└── Order Service continues processing

Total wait: 20ms
```

**Example: Creating an Order**
```javascript
// Order Service
async function createOrder(userId, items) {
    // Synchronous call to User Service
    const user = await fetch(`http://user-service/users/${userId}`);
    if (!user.active) {
        throw new Error('User not active');
    }

    // Synchronous call to Inventory Service
    const availability = await fetch('http://inventory-service/check', {
        method: 'POST',
        body: JSON.stringify({ items })
    });

    if (!availability.allAvailable) {
        throw new Error('Items not available');
    }

    // Synchronous call to Pricing Service
    const pricing = await fetch('http://pricing-service/calculate', {
        method: 'POST',
        body: JSON.stringify({ items })
    });

    // Create order
    const order = await database.orders.create({
        userId,
        items,
        total: pricing.total
    });

    return order;
}

// Latency: 5ms (user) + 5ms (inventory) + 5ms (pricing) = 15ms
// Problem: If any service is slow or down, order creation fails
```

**Advantages:**
```
✓ Simple to understand and implement
✓ Immediate feedback (success or failure)
✓ Strong consistency
✓ Easy to debug (clear request/response flow)
✓ Familiar programming model
```

**Disadvantages:**
```
✗ Tight runtime coupling (caller waits for callee)
✗ Cascading failures (if callee down, caller fails)
✗ Latency accumulation (sum of all calls)
✗ Reduced availability (all services must be available)
✗ Difficult to handle retries (duplicate requests)
```

#### gRPC

**High-performance RPC framework:**
```
Benefits over HTTP/REST:
├── Binary protocol (Protocol Buffers) vs JSON
├── HTTP/2 (multiplexing, header compression)
├── Strongly typed contracts
├── Bidirectional streaming
└── 7-10x faster than REST

Service Definition (.proto file):
syntax = "proto3";

service UserService {
    rpc GetUser (GetUserRequest) returns (User);
    rpc CreateUser (CreateUserRequest) returns (User);
}

message User {
    int32 id = 1;
    string username = 2;
    string email = 3;
}

Generated code provides type-safe clients
```

**Example: gRPC Service Communication**
```python
# Order Service using gRPC to call User Service
import grpc
import user_service_pb2
import user_service_pb2_grpc

def create_order(user_id, items):
    # Create gRPC channel
    channel = grpc.insecure_channel('user-service:50051')
    stub = user_service_pb2_grpc.UserServiceStub(channel)

    # Make synchronous RPC call
    try:
        user = stub.GetUser(user_service_pb2.GetUserRequest(id=user_id))
        if not user.active:
            raise Exception('User not active')

        # Continue order creation...

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise Exception('User not found')
        elif e.code() == grpc.StatusCode.UNAVAILABLE:
            raise Exception('User service unavailable')
        raise
```

**When to use gRPC:**
```
✓ Internal service-to-service communication
✓ Performance critical paths
✓ Real-time communication (streaming)
✓ Polyglot environments (multiple languages)
✓ Strong contract enforcement needed

✗ Browser clients (limited support)
✗ Human-readable debugging needed
✗ External public APIs (REST more standard)
```

### Asynchronous Communication

**Definition:** Client sends message and continues without waiting (non-blocking).

#### Message Queues

**Point-to-point messaging:**
```
Producer → Queue → Consumer

Order Service ──{OrderCreated}──→ [Queue] ──→ Email Service
                                      ↓
                                  Analytics Service

Order Service doesn't wait:
├── Publishes OrderCreated event
├── Continues immediately
├── No knowledge of consumers
└── Consumers process at their own pace
```

**Example: RabbitMQ Message Queue**
```python
# Order Service (Producer)
import pika

def create_order(user_id, items):
    # Create order in database
    order = database.orders.create({
        'userId': user_id,
        'items': items,
        'status': 'PENDING'
    })

    # Publish event to queue (non-blocking)
    connection = pika.BlockingConnection()
    channel = connection.channel()
    channel.queue_declare(queue='order_created')

    message = json.dumps({
        'orderId': order.id,
        'userId': user_id,
        'items': items,
        'timestamp': datetime.now().isoformat()
    })

    channel.basic_publish(
        exchange='',
        routing_key='order_created',
        body=message
    )

    connection.close()

    # Return immediately (don't wait for email, analytics, etc.)
    return order

# Email Service (Consumer)
def callback(ch, method, properties, body):
    message = json.loads(body)

    # Send order confirmation email
    send_email(
        to=get_user_email(message['userId']),
        subject='Order Confirmation',
        body=f"Your order {message['orderId']} has been received"
    )

    # Acknowledge message processed
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming
connection = pika.BlockingConnection()
channel = connection.channel()
channel.queue_declare(queue='order_created')
channel.basic_consume(queue='order_created', on_message_callback=callback)
channel.start_consuming()

# Benefits:
# - Order creation fast (doesn't wait for email)
# - Email Service can be down, queue retains messages
# - Can add new consumers without changing Order Service
```

#### Publish-Subscribe (Pub/Sub)

**One-to-many messaging:**
```
Publisher → Topic → [Subscriber 1, Subscriber 2, Subscriber 3, ...]

Order Service ──{OrderCreated}──→ [OrderTopic]
                                       ├──→ Email Service
                                       ├──→ Analytics Service
                                       ├──→ Inventory Service
                                       └──→ Notification Service

Each subscriber gets a copy of the message
```

**Example: Kafka Event Stream**
```python
# Order Service (Publisher)
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def create_order(user_id, items):
    order = database.orders.create({
        'userId': user_id,
        'items': items,
        'status': 'PENDING'
    })

    # Publish event to Kafka topic
    producer.send('order-events', {
        'eventType': 'OrderCreated',
        'orderId': order.id,
        'userId': user_id,
        'items': items,
        'timestamp': datetime.now().isoformat()
    })

    return order

# Email Service (Subscriber)
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'order-events',
    bootstrap_servers=['kafka:9092'],
    group_id='email-service',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    event = message.value

    if event['eventType'] == 'OrderCreated':
        send_confirmation_email(event['userId'], event['orderId'])

# Analytics Service (Subscriber)
consumer = KafkaConsumer(
    'order-events',
    bootstrap_servers=['kafka:9092'],
    group_id='analytics-service'
)

for message in consumer:
    event = message.value

    if event['eventType'] == 'OrderCreated':
        track_order_created(event)

# Inventory Service (Subscriber)
consumer = KafkaConsumer(
    'order-events',
    bootstrap_servers=['kafka:9092'],
    group_id='inventory-service'
)

for message in consumer:
    event = message.value

    if event['eventType'] == 'OrderCreated':
        reserve_inventory(event['items'])
```

**Advantages of Async:**
```
✓ Loose temporal coupling (services don't wait)
✓ Better fault tolerance (queue buffers failures)
✓ Natural load leveling (consumers process at their pace)
✓ Easy to add new consumers (no publisher changes)
✓ Supports event-driven architecture
```

**Disadvantages of Async:**
```
✗ Eventual consistency (not immediate)
✗ More complex error handling (no direct failure feedback)
✗ Difficult to debug (distributed flow)
✗ Message ordering challenges
✗ Requires message broker infrastructure
```

### Synchronous vs Asynchronous: When to Use What?

```
Use Synchronous (HTTP/REST/gRPC) when:
├── Need immediate response
├── Strong consistency required
├── Query operations (read data)
├── User waiting for result
└── Simple request-response flow

Examples:
├── Get user profile (user waiting)
├── Validate credit card (need immediate yes/no)
├── Check inventory (before showing to user)
└── Authentication (need immediate verification)

Use Asynchronous (Message Queue/Pub-Sub) when:
├── Fire-and-forget operations
├── Eventual consistency acceptable
├── Background processing
├── Multiple consumers need same event
└── Decouple services

Examples:
├── Send email (user doesn't wait)
├── Generate reports (background job)
├── Update analytics (eventual is fine)
├── Trigger notifications (multiple channels)
└── Process images/videos (time-consuming)
```

### Hybrid Approach

**Real-world systems use both:**
```
Order Creation Flow (Hybrid):

1. Synchronous validation:
   Order Service → User Service (verify user exists)
   Order Service → Inventory Service (check availability)
   Order Service → Pricing Service (calculate total)

   User waits for these (need immediate confirmation)

2. Asynchronous processing:
   Order Service → [Queue] → Email Service (send confirmation)
                          → Analytics Service (track metrics)
                          → Warehouse Service (prepare shipment)
                          → Recommendation Service (update ML model)

   User doesn't wait for these (background work)

Result:
├── Fast response to user (synchronous validation)
├── Resilient background processing (async events)
└── Best of both worlds
```

---

## 3. Service Mesh Concepts

### What is a Service Mesh?

**Definition:** A dedicated infrastructure layer for handling service-to-service communication, providing observability, security, and reliability features without requiring code changes.

**Problem it solves:**
```
Without Service Mesh:
Each service must implement:
├── Retry logic
├── Circuit breakers
├── Timeouts
├── Load balancing
├── Service discovery
├── Metrics collection
├── Distributed tracing
├── Mutual TLS
└── Rate limiting

Problem: Code duplication, polyglot challenges, inconsistent implementations

With Service Mesh:
├── Proxy handles all cross-cutting concerns
├── Services just send/receive messages
├── Consistent behavior across all services
└── Language-agnostic
```

### Architecture: Sidecar Pattern

**How it works:**
```
Traditional:
Service A ───────────────→ Service B

With Service Mesh:
Service A → Sidecar Proxy ═══→ Sidecar Proxy → Service B
            (Envoy)                (Envoy)

Each service gets a sidecar proxy:
├── Intercepts all network traffic
├── Applies policies (retries, timeouts, etc.)
├── Collects metrics
├── Enforces security
└── Routes traffic
```

### Service Mesh Components

#### Data Plane (Sidecar Proxies)

**Example: Envoy Proxy**
```
Responsibilities:
├── Traffic management
│   ├── Load balancing
│   ├── Retries with exponential backoff
│   ├── Timeouts
│   ├── Circuit breaking
│   └── Fault injection
├── Security
│   ├── mTLS (mutual TLS)
│   ├── Certificate management
│   └── Authentication
├── Observability
│   ├── Metrics (latency, error rates)
│   ├── Distributed tracing
│   └── Access logs
└── Service discovery
    └── Dynamic endpoint lookup
```

**Example Configuration: Retry Policy**
```yaml
# Envoy configuration (applied via service mesh control plane)
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
  - order-service
  http:
  - retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream
    timeout: 10s
    route:
    - destination:
        host: order-service

# Benefits:
# - No code changes to Order Service
# - Consistent retry behavior across all services
# - Can update policy without redeploying services
```

#### Control Plane

**Example: Istio Control Plane**
```
Components:
├── Pilot
│   ├── Service discovery
│   ├── Traffic management rules
│   └── Distributes config to proxies
├── Citadel
│   ├── Certificate authority
│   ├── Key and certificate management
│   └── Enforces mTLS
├── Galley
│   ├── Configuration validation
│   └── Ingestion and distribution
└── Mixer (deprecated in newer versions)
    ├── Policy enforcement
    └── Telemetry collection

Control plane tells data plane what to do
```

### Service Mesh Features

#### 1. Traffic Management

**Load Balancing Strategies:**
```yaml
# Route 90% to v1, 10% to v2 (canary deployment)
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
spec:
  hosts:
  - payment-service
  http:
  - match:
    - headers:
        user-type:
          exact: beta
    route:
    - destination:
        host: payment-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: payment-service
        subset: v1
      weight: 90
    - destination:
        host: payment-service
        subset: v2
      weight: 10
```

**Circuit Breaking:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: inventory-service
spec:
  host: inventory-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
```

#### 2. Security

**Automatic mTLS:**
```yaml
# Require mTLS for all services
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT

# Result:
# - All service-to-service communication encrypted
# - Automatic certificate rotation
# - No code changes required
```

**Authorization Policies:**
```yaml
# Only Order Service can call Payment Service
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/order-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/payments/*"]
```

#### 3. Observability

**Automatic Metrics:**
```
Service mesh automatically collects:
├── Request rate
├── Request latency (p50, p90, p99)
├── Error rate
├── Request size
└── Response size

For every service, no instrumentation needed

Prometheus metrics example:
istio_requests_total{
  source_app="order-service",
  destination_app="payment-service",
  response_code="200"
} = 1543

istio_request_duration_milliseconds{
  source_app="order-service",
  destination_app="payment-service",
  percentile="99"
} = 45.3
```

**Distributed Tracing:**
```
Service Mesh + Jaeger/Zipkin:

User Request → API Gateway
                    ↓ (trace-id: abc123)
              Order Service
                    ↓ (trace-id: abc123, span-id: 1)
              Inventory Service
                    ↓ (trace-id: abc123, span-id: 2)
              Payment Service

Trace shows:
├── Total request time: 150ms
├── Order Service: 100ms (including downstream calls)
│   ├── Inventory Service: 30ms
│   └── Payment Service: 50ms
└── Identified bottleneck: Payment Service
```

### Popular Service Mesh Options

```
Istio:
├── Most feature-rich
├── Steep learning curve
├── Envoy-based
├── Strong Google/IBM backing
└── Best for: Large enterprises, complex requirements

Linkerd:
├── Lightweight
├── Easy to get started
├── Rust-based proxy
├── CNCF graduated project
└── Best for: Simplicity, performance

Consul Connect:
├── HashiCorp ecosystem integration
├── Works with Envoy
├── Multi-cloud focus
└── Best for: HashiCorp users, hybrid cloud

AWS App Mesh:
├── AWS-native
├── Envoy-based
├── Integrates with AWS services
└── Best for: AWS environments
```

### When to Use Service Mesh

**Good fit:**
```
✓ Large number of microservices (10+)
✓ Complex traffic management needs
✓ Security requirements (mTLS, authorization)
✓ Need uniform observability
✓ Polyglot architecture (multiple languages)
✓ Kubernetes-based deployments
```

**Not needed:**
```
✗ Small number of services (< 10)
✗ Simple architectures
✗ Team lacks Kubernetes expertise
✗ Performance overhead unacceptable
✗ Additional complexity not justified
```

---

## 4. API Gateway Pattern

### What is an API Gateway?

**Definition:** A single entry point for all client requests, routing them to appropriate microservices and providing cross-cutting functionality.

**Analogy:** Like a receptionist in a building who directs visitors to the right department.

### Problem Without API Gateway

```
Mobile App needs to display order details:

Without Gateway:
Mobile App ──→ User Service (get user info)
          ──→ Order Service (get order details)
          ──→ Product Service (get product info)
          ──→ Inventory Service (get stock status)
          ──→ Shipping Service (get tracking)

Problems:
├── Mobile app knows about 5 services
├── 5 separate network calls (slow, battery drain)
├── Complex client logic
├── Difficult to change backend without updating apps
├── No centralized authentication
└── No unified error handling
```

**With API Gateway:**
```
Mobile App ──→ API Gateway ──┬──→ User Service
                             ├──→ Order Service
                             ├──→ Product Service
                             ├──→ Inventory Service
                             └──→ Shipping Service
            ←─── Aggregated Response

Benefits:
├── Single endpoint for mobile app
├── 1 network call instead of 5
├── Gateway handles service discovery
├── Centralized authentication
└── Backend can change without app updates
```

### API Gateway Responsibilities

#### 1. Request Routing

```
Route based on path:

GET /api/users/123        → User Service
GET /api/products/456     → Product Service
POST /api/orders          → Order Service
GET /api/orders/789       → Order Service

Route based on headers:

GET /api/products
  User-Agent: mobile      → Product Service v2 (mobile-optimized)
  User-Agent: desktop     → Product Service v1 (full data)

Route based on version:

GET /v1/api/orders        → Order Service v1
GET /v2/api/orders        → Order Service v2
```

**Example: Kong Gateway Configuration**
```yaml
# Route configuration
services:
  - name: user-service
    url: http://user-service:8080
    routes:
      - name: user-route
        paths:
          - /api/users

  - name: order-service
    url: http://order-service:8080
    routes:
      - name: order-route
        paths:
          - /api/orders

  - name: product-service
    url: http://product-service:8080
    routes:
      - name: product-route
        paths:
          - /api/products
```

#### 2. Request Aggregation (Backend for Frontend Pattern)

**Scenario: Display user dashboard**
```javascript
// Without aggregation (client makes multiple calls)
const user = await fetch('/api/users/123');
const orders = await fetch('/api/orders?userId=123');
const recommendations = await fetch('/api/recommendations?userId=123');
const notifications = await fetch('/api/notifications?userId=123');

// 4 round trips, slow on mobile

// With aggregation (API Gateway endpoint)
// GET /api/dashboard/123

// API Gateway implementation:
async function getDashboard(userId) {
    // Gateway makes calls in parallel
    const [user, orders, recommendations, notifications] = await Promise.all([
        fetch(`http://user-service/users/${userId}`),
        fetch(`http://order-service/orders?userId=${userId}`),
        fetch(`http://recommendation-service/recommendations?userId=${userId}`),
        fetch(`http://notification-service/notifications?userId=${userId}`)
    ]);

    // Aggregate into single response
    return {
        user: {
            name: user.name,
            email: user.email
        },
        recentOrders: orders.slice(0, 5),
        recommendations: recommendations.slice(0, 10),
        unreadNotifications: notifications.filter(n => !n.read).length
    };
}

// Client gets everything in 1 call
```

#### 3. Authentication and Authorization

**Centralized security:**
```
Flow:
1. Client ──(request with JWT)──→ API Gateway
2. Gateway validates JWT
3. If valid: Extract user info, forward to service
   If invalid: Return 401 Unauthorized

Benefits:
├── Services don't need to validate tokens
├── Consistent auth across all services
├── Easy to update auth mechanism
└── Can add/remove services without auth changes
```

**Example: JWT Validation in API Gateway**
```javascript
// API Gateway middleware
async function authenticateRequest(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }

    try {
        // Verify JWT
        const decoded = jwt.verify(token, process.env.JWT_SECRET);

        // Add user info to request
        req.user = {
            id: decoded.userId,
            role: decoded.role
        };

        // Forward to backend service
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Invalid token' });
    }
}

// Apply to all routes
app.use('/api/*', authenticateRequest);

// Services receive authenticated requests:
// headers: { 'X-User-Id': '123', 'X-User-Role': 'customer' }
```

#### 4. Rate Limiting

**Prevent abuse:**
```yaml
# Kong rate limiting plugin
plugins:
  - name: rate-limiting
    config:
      minute: 100        # 100 requests per minute
      hour: 5000         # 5000 requests per hour
      policy: local      # Or 'redis' for distributed
      fault_tolerant: true
      hide_client_headers: false
```

**Example: Tiered Rate Limiting**
```javascript
// Different limits for different user tiers
async function rateLimitMiddleware(req, res, next) {
    const userId = req.user.id;
    const tier = req.user.tier; // 'free', 'premium', 'enterprise'

    const limits = {
        free: 100,        // 100 requests/hour
        premium: 1000,    // 1000 requests/hour
        enterprise: 10000 // 10000 requests/hour
    };

    const key = `ratelimit:${userId}`;
    const current = await redis.incr(key);

    if (current === 1) {
        await redis.expire(key, 3600); // 1 hour TTL
    }

    if (current > limits[tier]) {
        return res.status(429).json({
            error: 'Rate limit exceeded',
            limit: limits[tier],
            reset: await redis.ttl(key)
        });
    }

    res.setHeader('X-RateLimit-Limit', limits[tier]);
    res.setHeader('X-RateLimit-Remaining', limits[tier] - current);

    next();
}
```

#### 5. Response Transformation

**Adapt backend responses for clients:**
```javascript
// Backend returns verbose response
{
    "userId": 123,
    "userName": "alice",
    "userEmailAddress": "alice@example.com",
    "orderIdentifier": "ORD-2024-001",
    "orderStatus": "SHIPPED",
    "orderItems": [...],
    "internalMetadata": {...}
}

// API Gateway transforms for mobile (minimal data)
{
    "id": 123,
    "name": "alice",
    "order": {
        "id": "ORD-2024-001",
        "status": "shipped"
    }
}

// Implementation
function transformForMobile(backendResponse) {
    return {
        id: backendResponse.userId,
        name: backendResponse.userName,
        order: {
            id: backendResponse.orderIdentifier,
            status: backendResponse.orderStatus.toLowerCase()
        }
    };
}
```

#### 6. Caching

**Cache common responses:**
```javascript
// API Gateway caching
async function cacheMiddleware(req, res, next) {
    // Only cache GET requests
    if (req.method !== 'GET') {
        return next();
    }

    const cacheKey = `cache:${req.url}`;
    const cached = await redis.get(cacheKey);

    if (cached) {
        res.setHeader('X-Cache', 'HIT');
        return res.json(JSON.parse(cached));
    }

    // Store original res.json
    const originalJson = res.json.bind(res);

    // Override res.json to cache response
    res.json = function(data) {
        redis.setex(cacheKey, 300, JSON.stringify(data)); // Cache 5 minutes
        res.setHeader('X-Cache', 'MISS');
        originalJson(data);
    };

    next();
}

// Product catalog rarely changes, cache aggressively
app.get('/api/products', cacheMiddleware, async (req, res) => {
    const products = await fetch('http://product-service/products');
    res.json(products);
});
```

### API Gateway Patterns

#### Backend for Frontend (BFF)

**Different gateways for different clients:**
```
Mobile App ──→ Mobile BFF ──┬──→ User Service
                            ├──→ Order Service
                            └──→ Product Service

Web App ──→ Web BFF ──┬──→ User Service
                      ├──→ Order Service
                      ├──→ Product Service
                      └──→ Analytics Service

Partner API ──→ Partner BFF ──→ Limited Services

Each BFF optimized for its client:
├── Mobile BFF: Minimal payloads, image optimization
├── Web BFF: Rich data, pagination
└── Partner BFF: Rate limiting, specific endpoints
```

**Example: Mobile BFF vs Web BFF**
```javascript
// Mobile BFF: /api/mobile/products
async function getMobileProducts(req, res) {
    const products = await fetch('http://product-service/products');

    // Optimize for mobile
    const mobileResponse = products.map(p => ({
        id: p.id,
        name: p.name,
        price: p.price,
        thumbnail: p.images[0].thumbnail, // Small image only
        inStock: p.inventory > 0
    }));

    res.json(mobileResponse);
}

// Web BFF: /api/web/products
async function getWebProducts(req, res) {
    const products = await fetch('http://product-service/products');

    // Full data for web
    const webResponse = products.map(p => ({
        id: p.id,
        name: p.name,
        description: p.description,
        price: p.price,
        images: p.images, // All images
        inventory: p.inventory,
        specifications: p.specs,
        reviews: p.reviews
    }));

    res.json(webResponse);
}
```

### Popular API Gateway Solutions

```
Kong:
├── Open source
├── Plugin-based architecture
├── High performance (Nginx + Lua)
├── Extensive plugin ecosystem
└── Best for: Feature-rich gateway needs

AWS API Gateway:
├── Fully managed
├── Serverless (Lambda integration)
├── Auto-scaling
├── Pay per request
└── Best for: AWS-native architectures

Envoy:
├── C++ based, very fast
├── Service mesh integration
├── Advanced traffic management
└── Best for: Complex routing, observability

Spring Cloud Gateway:
├── Java-based
├── Spring ecosystem integration
├── Reactive (WebFlux)
└── Best for: Spring Boot microservices

NGINX:
├── Battle-tested
├── Reverse proxy + API gateway
├── High performance
└── Best for: Simple routing, load balancing
```

### API Gateway Anti-Patterns

#### God Gateway

**Problem:**
```
API Gateway becomes monolith:
├── Business logic in gateway
├── Database queries in gateway
├── Complex data transformation
├── Stateful operations
└── Becomes bottleneck

Better: Gateway should be thin, routing only
```

#### Too Many Gateways

**Problem:**
```
One gateway per service:
├── Service A Gateway
├── Service B Gateway
├── Service C Gateway
...

Result: Clients still need to know about multiple gateways

Better: Single gateway (or BFF pattern for different client types)
```

---

## Summary

### Key Takeaways

**Service Boundaries:**
- Use Domain-Driven Design to find natural boundaries
- Services should be right-sized (not too small, not too large)
- Each service represents a complete business capability
- Boundaries wrong = frequent cross-service changes

**Communication Patterns:**
- Synchronous (HTTP/gRPC): Immediate response, strong consistency
- Asynchronous (Queues/Pub-Sub): Decoupling, eventual consistency
- Most systems use hybrid approach
- Choose based on business requirements

**Service Mesh:**
- Infrastructure layer for service communication
- Provides observability, security, reliability
- Sidecar proxy per service
- Best for: 10+ services, complex requirements

**API Gateway:**
- Single entry point for clients
- Routing, aggregation, authentication
- Backend for Frontend pattern for different clients
- Should be thin layer, not business logic

### Real-World Architecture Example

**E-commerce System:**
```
                    [API Gateway]
                         |
        +----------------+----------------+
        |                |                |
   [Mobile BFF]     [Web BFF]    [Partner API]
        |                |                |
        +----------------+----------------+
                         |
              [Service Mesh (Istio)]
                         |
        +-------+--------+--------+-------+
        |       |        |        |       |
      User   Product  Order   Payment Shipping
    Service  Service Service  Service  Service
        |       |        |        |       |
      [DB]    [DB]     [DB]     [DB]    [DB]

Communication:
├── Sync: API calls for immediate data (gRPC)
├── Async: Events for background work (Kafka)
└── Service Mesh: Handles all cross-cutting concerns
```

---

## Further Reading

**Books:**
- "Building Microservices" by Sam Newman (2nd Edition)
- "Microservices Patterns" by Chris Richardson
- "Production-Ready Microservices" by Susan Fowler

**Online Resources:**
- microservices.io (Chris Richardson's patterns catalog)
- Martin Fowler's microservices articles
- Istio.io documentation
- Kong documentation

**Next Topics:**
- Event-Driven Architecture
- Data management in microservices
- Testing microservices
- Deployment strategies

---

**Remember:** Microservices introduce complexity. Only adopt them when the benefits (independent deployment, scaling, technology choice) outweigh the costs (operational overhead, distributed system challenges). Many successful systems start as monoliths and evolve to microservices as needs dictate.
