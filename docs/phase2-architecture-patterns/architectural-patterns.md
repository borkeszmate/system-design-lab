# Architectural Patterns

## Overview

Beyond microservices and event-driven architecture, several fundamental architectural patterns help organize code and system structure. These patterns provide different perspectives on separating concerns, managing dependencies, and organizing layers of abstraction.

This document covers four important patterns:
1. **Layered Architecture** - Organizing code by technical responsibility
2. **Hexagonal Architecture** (Ports & Adapters) - Isolating business logic
3. **Clean Architecture** - Dependency rule and concentric layers
4. **Strangler Fig Pattern** - Incrementally migrating legacy systems

Understanding these patterns helps you make better architectural decisions and communicate designs effectively.

---

## 1. Layered Architecture

### What is Layered Architecture?

**Definition:** Organizing code into horizontal layers where each layer has a specific responsibility and depends only on layers below it.

**Key Principle:** **Separation of concerns** by technical function.

### Traditional 3-Tier Architecture

```
┌─────────────────────────────┐
│   Presentation Layer        │  ← User interface, API endpoints
├─────────────────────────────┤
│   Business Logic Layer      │  ← Business rules, domain logic
├─────────────────────────────┤
│   Data Access Layer         │  ← Database operations, queries
└─────────────────────────────┘

Dependency flow: Top → Bottom
Presentation depends on Business Logic
Business Logic depends on Data Access
```

### Layer Responsibilities

#### Presentation Layer (UI/API)

**Responsibilities:**
- Handle HTTP requests/responses
- Input validation (format, not business rules)
- Serialize/deserialize data (JSON, XML)
- Authentication/authorization
- Routing

**Should NOT:**
- Contain business logic
- Access database directly
- Make business decisions

**Example: REST API Controller**
```python
# Presentation Layer
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/orders', methods=['POST'])
def create_order():
    # 1. Parse request
    data = request.json

    # 2. Validate format (not business rules)
    if not data.get('user_id') or not data.get('items'):
        return jsonify({'error': 'Missing required fields'}), 400

    # 3. Call business logic layer
    try:
        order = order_service.create_order(
            user_id=data['user_id'],
            items=data['items']
        )

        # 4. Format response
        return jsonify({
            'order_id': order.id,
            'status': order.status,
            'total': order.total
        }), 201

    except BusinessException as e:
        return jsonify({'error': str(e)}), 400

# Thin layer: Just handles HTTP, delegates to business logic
```

#### Business Logic Layer (Domain/Service)

**Responsibilities:**
- Business rules and validation
- Orchestrate use cases
- Domain calculations
- Transaction coordination

**Should NOT:**
- Know about HTTP, JSON, or UI concerns
- Directly use database libraries (uses abstraction)
- Depend on infrastructure details

**Example: Order Service**
```python
# Business Logic Layer
class OrderService:
    def __init__(self, order_repository, inventory_service, pricing_service):
        self.order_repo = order_repository
        self.inventory = inventory_service
        self.pricing = pricing_service

    def create_order(self, user_id, items):
        # Business rule: User must exist and be active
        user = self.order_repo.get_user(user_id)
        if not user or not user.is_active:
            raise BusinessException('User not found or inactive')

        # Business rule: Items must be in stock
        for item in items:
            if not self.inventory.is_available(item['product_id'], item['quantity']):
                raise BusinessException(f'Product {item["product_id"]} not available')

        # Business calculation: Calculate total
        total = self.pricing.calculate_total(items)

        # Business rule: Minimum order amount
        if total < 10:
            raise BusinessException('Minimum order amount is $10')

        # Create order (via data access abstraction)
        order = Order(
            user_id=user_id,
            items=items,
            total=total,
            status='PENDING'
        )

        # Persist
        self.order_repo.save(order)

        # Business process: Reserve inventory
        self.inventory.reserve(order.id, items)

        return order

# Contains ALL business logic, no infrastructure knowledge
```

#### Data Access Layer (Repository/DAO)

**Responsibilities:**
- Database queries
- ORM mapping
- Transaction management
- Database-specific optimizations

**Should NOT:**
- Contain business logic
- Make business decisions
- Know about HTTP or UI

**Example: Order Repository**
```python
# Data Access Layer
class OrderRepository:
    def __init__(self, database):
        self.db = database

    def save(self, order):
        """Persist order to database"""
        with self.db.transaction():
            self.db.execute("""
                INSERT INTO orders (id, user_id, total, status, created_at)
                VALUES (:id, :user_id, :total, :status, :created_at)
            """, {
                'id': order.id,
                'user_id': order.user_id,
                'total': order.total,
                'status': order.status,
                'created_at': order.created_at
            })

            # Save order items
            for item in order.items:
                self.db.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (:order_id, :product_id, :quantity, :price)
                """, {
                    'order_id': order.id,
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': item['price']
                })

    def get_by_id(self, order_id):
        """Retrieve order from database"""
        result = self.db.query("""
            SELECT id, user_id, total, status, created_at
            FROM orders
            WHERE id = :id
        """, {'id': order_id})

        if not result:
            return None

        # Load items
        items = self.db.query("""
            SELECT product_id, quantity, price
            FROM order_items
            WHERE order_id = :order_id
        """, {'order_id': order_id})

        return Order(
            id=result['id'],
            user_id=result['user_id'],
            items=items,
            total=result['total'],
            status=result['status'],
            created_at=result['created_at']
        )

    def get_user(self, user_id):
        """Helper to get user (could be separate UserRepository)"""
        result = self.db.query("""
            SELECT id, email, is_active
            FROM users
            WHERE id = :id
        """, {'id': user_id})

        return User(**result) if result else None

# Pure data access, no business logic
```

### Complete Layered Example

```python
# ============================================
# Presentation Layer (API)
# ============================================
from flask import Flask, request, jsonify

app = Flask(__name__)

# Dependency injection (could use DI framework)
database = Database('postgresql://localhost/ecommerce')
order_repository = OrderRepository(database)
inventory_service = InventoryService()
pricing_service = PricingService()
order_service = OrderService(order_repository, inventory_service, pricing_service)

@app.route('/api/orders', methods=['POST'])
def create_order_endpoint():
    data = request.json

    try:
        order = order_service.create_order(
            user_id=data['user_id'],
            items=data['items']
        )

        return jsonify({
            'order_id': order.id,
            'status': order.status,
            'total': order.total
        }), 201

    except BusinessException as e:
        return jsonify({'error': str(e)}), 400


# ============================================
# Business Logic Layer (Service)
# ============================================
class OrderService:
    def __init__(self, order_repository, inventory_service, pricing_service):
        self.order_repo = order_repository
        self.inventory = inventory_service
        self.pricing = pricing_service

    def create_order(self, user_id, items):
        # Business validation
        user = self.order_repo.get_user(user_id)
        if not user or not user.is_active:
            raise BusinessException('User not found or inactive')

        # Check inventory
        for item in items:
            if not self.inventory.is_available(item['product_id'], item['quantity']):
                raise BusinessException(f'Product {item["product_id"]} not available')

        # Calculate total
        total = self.pricing.calculate_total(items)

        if total < 10:
            raise BusinessException('Minimum order amount is $10')

        # Create and save order
        order = Order(
            user_id=user_id,
            items=items,
            total=total,
            status='PENDING'
        )

        self.order_repo.save(order)
        self.inventory.reserve(order.id, items)

        return order


# ============================================
# Data Access Layer (Repository)
# ============================================
class OrderRepository:
    def __init__(self, database):
        self.db = database

    def save(self, order):
        with self.db.transaction():
            self.db.execute("""
                INSERT INTO orders (id, user_id, total, status, created_at)
                VALUES (:id, :user_id, :total, :status, :created_at)
            """, order.__dict__)

    def get_by_id(self, order_id):
        result = self.db.query("""
            SELECT * FROM orders WHERE id = :id
        """, {'id': order_id})

        return Order(**result) if result else None

    def get_user(self, user_id):
        result = self.db.query("""
            SELECT * FROM users WHERE id = :id
        """, {'id': user_id})

        return User(**result) if result else None
```

### Benefits of Layered Architecture

```
✓ Clear separation of concerns
  ├── Easy to find code (know which layer)
  ├── Each layer has specific purpose
  └── Reduces complexity

✓ Easy to understand
  ├── Natural flow (top to bottom)
  ├── Familiar pattern
  └── Low learning curve

✓ Easy to test
  ├── Mock layers below
  ├── Test business logic without database
  └── Test API without business logic

✓ Easy to replace layers
  ├── Swap database (change data layer)
  ├── Swap UI (change presentation)
  └── Business logic unchanged
```

### Drawbacks of Layered Architecture

```
✗ Coupling to database
  ├── Business logic layer depends on data layer
  ├── Database structure leaks upward
  └── Hard to test business logic in isolation

✗ Horizontal slicing
  ├── Features span all layers
  ├── Change requires modifying all layers
  └── No clear feature boundaries

✗ Tendency toward anemic domain model
  ├── Logic in service layer, not domain objects
  ├── Domain objects become data bags
  └── Not object-oriented

✗ Rigid structure
  ├── Sometimes layers are artificial
  ├── Forces code into layers even when not natural
  └── Can lead to over-engineering
```

### Layered Architecture Variants

#### Relaxed Layered Architecture

**Allows skipping layers:**
```
Traditional (strict):
Presentation → Business → Data

Relaxed:
Presentation → Business → Data
     └──────────────→ Data (can skip business layer for simple queries)

When to skip: Read-only queries, reporting
Example: Presentation directly queries database for dashboard
```

#### N-Tier Architecture

**Physical separation of layers:**
```
Client Tier (Browser, Mobile App)
      ↓
Application Server Tier (API, Business Logic)
      ↓
Database Server Tier (PostgreSQL, MySQL)

Each tier on different machine
Benefits: Scalability, security
Drawbacks: Network latency, complexity
```

---

## 2. Hexagonal Architecture (Ports & Adapters)

### What is Hexagonal Architecture?

**Definition:** Architecture where business logic (domain) is at the center, isolated from external concerns via ports and adapters.

**Also known as:** Ports and Adapters Pattern

**Key Idea:** Protect business logic from external dependencies.

### Core Concepts

```
              ┌─────────────────┐
              │   Application   │
              │   (Use Cases)   │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼───┐   ┌────▼───┐   ┌─────▼────┐
    │ Ports  │   │ Ports  │   │  Ports   │
    │(Interf)│   │(Interf)│   │ (Interf) │
    └────┬───┘   └────┬───┘   └─────┬────┘
         │            │              │
    ┌────▼───┐   ┌───▼────┐   ┌─────▼────┐
    │HTTP    │   │Database│   │  Email   │
    │Adapter │   │Adapter │   │ Adapter  │
    └────────┘   └────────┘   └──────────┘

Business logic in center
Ports: Interfaces
Adapters: Implementations
```

**Components:**

1. **Domain (Hexagon Center):** Business logic, domain entities
2. **Ports:** Interfaces (what the application needs)
3. **Adapters:** Implementations (how we fulfill needs)

### Ports

**Definition:** Interfaces that define what the application needs from the outside world.

**Types:**

**Inbound/Driving Ports:** How the outside world calls the application
```python
# Inbound port (interface)
class OrderService(ABC):
    """Port: Interface for creating orders"""

    @abstractmethod
    def create_order(self, user_id: int, items: List[OrderItem]) -> Order:
        """Create a new order"""
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> Order:
        """Retrieve an order"""
        pass
```

**Outbound/Driven Ports:** How the application calls external systems
```python
# Outbound port (interface)
class OrderRepository(ABC):
    """Port: Interface for persisting orders"""

    @abstractmethod
    def save(self, order: Order) -> None:
        """Persist order"""
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """Find order by ID"""
        pass


class PaymentGateway(ABC):
    """Port: Interface for processing payments"""

    @abstractmethod
    def charge(self, amount: Decimal, card_token: str) -> PaymentResult:
        """Charge a payment"""
        pass
```

### Adapters

**Definition:** Concrete implementations of ports.

**Inbound Adapters (Driving):** REST API, GraphQL, CLI, Message Queue

**Example: REST Adapter**
```python
# Inbound adapter: REST API
from flask import Flask, request, jsonify

class RestOrderAdapter:
    """Adapter: REST API implementation"""

    def __init__(self, order_service: OrderService):
        self.order_service = order_service
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/orders', methods=['POST'])
        def create_order():
            data = request.json

            # Translate REST to domain
            items = [
                OrderItem(product_id=item['product_id'], quantity=item['quantity'])
                for item in data['items']
            ]

            # Call domain through port
            order = self.order_service.create_order(
                user_id=data['user_id'],
                items=items
            )

            # Translate domain to REST
            return jsonify({
                'id': order.id,
                'status': order.status,
                'total': str(order.total)
            }), 201
```

**Outbound Adapters (Driven):** PostgreSQL, MongoDB, Stripe, SendGrid

**Example: PostgreSQL Adapter**
```python
# Outbound adapter: PostgreSQL repository
class PostgresOrderRepository(OrderRepository):
    """Adapter: PostgreSQL implementation of OrderRepository port"""

    def __init__(self, database):
        self.db = database

    def save(self, order: Order) -> None:
        self.db.execute("""
            INSERT INTO orders (id, user_id, total, status)
            VALUES (:id, :user_id, :total, :status)
        """, {
            'id': order.id,
            'user_id': order.user_id,
            'total': order.total,
            'status': order.status
        })

    def find_by_id(self, order_id: str) -> Optional[Order]:
        result = self.db.query("""
            SELECT id, user_id, total, status
            FROM orders
            WHERE id = :id
        """, {'id': order_id})

        if not result:
            return None

        return Order(
            id=result['id'],
            user_id=result['user_id'],
            total=Decimal(result['total']),
            status=result['status']
        )


# Outbound adapter: Stripe payment
class StripePaymentGateway(PaymentGateway):
    """Adapter: Stripe implementation of PaymentGateway port"""

    def __init__(self, api_key: str):
        self.stripe = stripe
        self.stripe.api_key = api_key

    def charge(self, amount: Decimal, card_token: str) -> PaymentResult:
        try:
            charge = self.stripe.Charge.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                source=card_token
            )

            return PaymentResult(
                success=True,
                transaction_id=charge.id
            )
        except stripe.error.CardError as e:
            return PaymentResult(
                success=False,
                error=str(e)
            )
```

### Complete Hexagonal Example

```python
# ============================================
# DOMAIN (Center of Hexagon)
# ============================================
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

@dataclass
class Order:
    """Domain entity"""
    id: str
    user_id: int
    items: List['OrderItem']
    total: Decimal
    status: str

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    price: Decimal


# ============================================
# PORTS (Interfaces)
# ============================================
from abc import ABC, abstractmethod

# Inbound port
class OrderService(ABC):
    @abstractmethod
    def create_order(self, user_id: int, items: List[OrderItem]) -> Order:
        pass

# Outbound ports
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        pass

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: Decimal, card_token: str) -> bool:
        pass


# ============================================
# APPLICATION (Use Cases)
# ============================================
class OrderServiceImpl(OrderService):
    """Application logic (implements inbound port)"""

    def __init__(self, order_repository: OrderRepository, payment_gateway: PaymentGateway):
        # Depends on outbound ports (interfaces), not implementations
        self.order_repo = order_repository
        self.payment = payment_gateway

    def create_order(self, user_id: int, items: List[OrderItem]) -> Order:
        # Business logic
        total = sum(item.price * item.quantity for item in items)

        if total < 10:
            raise ValueError('Minimum order is $10')

        # Create order
        order = Order(
            id=generate_uuid(),
            user_id=user_id,
            items=items,
            total=total,
            status='PENDING'
        )

        # Use outbound port (doesn't know if it's Postgres, Mongo, etc.)
        self.order_repo.save(order)

        return order


# ============================================
# ADAPTERS (Implementations)
# ============================================

# Inbound adapter: REST API
class RestOrderAdapter:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service

    def create_order_endpoint(self, request_data):
        items = [
            OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=Decimal(item['price'])
            )
            for item in request_data['items']
        ]

        order = self.order_service.create_order(
            user_id=request_data['user_id'],
            items=items
        )

        return {'order_id': order.id, 'total': str(order.total)}


# Outbound adapter: PostgreSQL
class PostgresOrderRepository(OrderRepository):
    def __init__(self, database):
        self.db = database

    def save(self, order: Order) -> None:
        self.db.execute("""
            INSERT INTO orders (id, user_id, total, status)
            VALUES (:id, :user_id, :total, :status)
        """, order.__dict__)

    def find_by_id(self, order_id: str) -> Optional[Order]:
        # ... query database ...
        pass


# Outbound adapter: Stripe
class StripePaymentGateway(PaymentGateway):
    def charge(self, amount: Decimal, card_token: str) -> bool:
        # ... call Stripe API ...
        pass


# ============================================
# WIRING (Dependency Injection)
# ============================================
# Create adapters
database = Database('postgresql://...')
order_repo = PostgresOrderRepository(database)
payment_gateway = StripePaymentGateway(api_key='sk_test_...')

# Create application (inject dependencies via ports)
order_service = OrderServiceImpl(order_repo, payment_gateway)

# Create inbound adapter
rest_adapter = RestOrderAdapter(order_service)

# Application doesn't know about Postgres or Stripe
# Can swap to MongoDB or PayPal without changing business logic!
```

### Benefits of Hexagonal Architecture

```
✓ Technology independent
  ├── Business logic doesn't know about database, API, etc.
  ├── Easy to swap implementations
  └── Can delay technology choices

✓ Highly testable
  ├── Test business logic with mocks
  ├── No need for database or external services
  └── Fast unit tests

✓ Flexibility
  ├── Multiple adapters for same port
  ├── REST and GraphQL adapters for same service
  └── Postgres and MongoDB adapters for same repository

✓ Clean dependencies
  ├── Dependencies point inward
  ├── Business logic has no external dependencies
  └── Outer layers depend on inner, not vice versa
```

### When to Use Hexagonal Architecture

```
Good fit:
✓ Complex business logic
✓ Multiple integration points
✓ Long-lived applications
✓ Need to swap technologies
✓ Testing is critical

Not needed:
✗ Simple CRUD applications
✗ Prototypes
✗ Single external dependency
✗ Team unfamiliar with pattern
```

---

## 3. Clean Architecture

### What is Clean Architecture?

**Definition:** An architecture pattern with concentric layers where dependencies point inward, and the innermost layer contains business rules.

**Created by:** Robert C. Martin (Uncle Bob)

**Key Principle:** The Dependency Rule - dependencies point inward toward business logic.

### The Concentric Circles

```
┌───────────────────────────────────────┐
│  Frameworks & Drivers (Web, DB, UI)  │  ← Outermost
├───────────────────────────────────────┤
│  Interface Adapters (Controllers,    │
│  Gateways, Presenters)                │
├───────────────────────────────────────┤
│  Use Cases (Application Business      │
│  Rules)                               │
├───────────────────────────────────────┤
│  Entities (Enterprise Business Rules) │  ← Innermost
└───────────────────────────────────────┘

Dependency Rule: Outer layers depend on inner, never the reverse
```

### Layers Explained

#### 1. Entities (Innermost Layer)

**What:** Enterprise-wide business rules and data structures.

**Characteristics:**
- Pure business logic
- No dependencies on anything
- Most stable, least likely to change

**Example:**
```python
# Entities layer
class Order:
    """Enterprise business rules"""

    def __init__(self, id: str, user_id: int, items: List[OrderItem]):
        self.id = id
        self.user_id = user_id
        self.items = items
        self._status = 'DRAFT'

    def calculate_total(self) -> Decimal:
        """Business rule: Total is sum of item prices"""
        return sum(item.price * item.quantity for item in self.items)

    def confirm(self) -> None:
        """Business rule: Can only confirm draft orders"""
        if self._status != 'DRAFT':
            raise ValueError('Can only confirm draft orders')

        if not self.items:
            raise ValueError('Cannot confirm empty order')

        if self.calculate_total() < Decimal('10.00'):
            raise ValueError('Minimum order total is $10')

        self._status = 'CONFIRMED'

    def cancel(self) -> None:
        """Business rule: Cannot cancel shipped orders"""
        if self._status == 'SHIPPED':
            raise ValueError('Cannot cancel shipped order')

        self._status = 'CANCELLED'

    @property
    def status(self) -> str:
        return self._status

# No dependencies, pure business logic
```

#### 2. Use Cases (Application Business Rules)

**What:** Application-specific business rules (use cases).

**Characteristics:**
- Orchestrate flow of data to/from entities
- Implement application-specific rules
- Depend only on entities

**Example:**
```python
# Use Cases layer
from typing import Protocol

# Define interfaces for dependencies (pointing inward)
class OrderRepository(Protocol):
    """Interface for outward dependency"""
    def save(self, order: Order) -> None: ...
    def find_by_id(self, order_id: str) -> Optional[Order]: ...

class PaymentGateway(Protocol):
    def process_payment(self, amount: Decimal, user_id: int) -> bool: ...

# Use case
class CreateOrderUseCase:
    """Application-specific business rule"""

    def __init__(self, order_repo: OrderRepository, payment: PaymentGateway):
        self.order_repo = order_repo
        self.payment = payment

    def execute(self, user_id: int, items: List[OrderItem]) -> str:
        # Create entity
        order = Order(
            id=generate_uuid(),
            user_id=user_id,
            items=items
        )

        # Apply business rule (in entity)
        order.confirm()

        # Process payment
        if not self.payment.process_payment(order.calculate_total(), user_id):
            raise PaymentFailedException()

        # Persist
        self.order_repo.save(order)

        return order.id

# Depends only on entities and interfaces (pointing inward)
```

#### 3. Interface Adapters (Controllers, Presenters, Gateways)

**What:** Convert data between use cases and external world.

**Characteristics:**
- Translate from external format to use case format
- Implement interfaces defined in use cases
- Depend on use cases

**Example:**
```python
# Interface Adapters layer

# Controller (converts REST to use case)
class OrderController:
    """Adapter: REST → Use Case"""

    def __init__(self, create_order_use_case: CreateOrderUseCase):
        self.create_order = create_order_use_case

    def handle_create_order(self, request_data: dict) -> dict:
        # Convert REST request to use case input
        items = [
            OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=Decimal(item['price'])
            )
            for item in request_data['items']
        ]

        # Execute use case
        order_id = self.create_order.execute(
            user_id=request_data['user_id'],
            items=items
        )

        # Convert use case output to REST response
        return {
            'order_id': order_id,
            'message': 'Order created successfully'
        }


# Gateway (implements repository interface)
class PostgresOrderRepository:
    """Adapter: Use Case Interface → Database"""

    def __init__(self, database):
        self.db = database

    def save(self, order: Order) -> None:
        # Convert entity to database format
        self.db.execute("""
            INSERT INTO orders (id, user_id, status, total)
            VALUES (:id, :user_id, :status, :total)
        """, {
            'id': order.id,
            'user_id': order.user_id,
            'status': order.status,
            'total': order.calculate_total()
        })

    def find_by_id(self, order_id: str) -> Optional[Order]:
        result = self.db.query("""
            SELECT id, user_id, status, items
            FROM orders WHERE id = :id
        """, {'id': order_id})

        if not result:
            return None

        # Convert database format to entity
        return Order(
            id=result['id'],
            user_id=result['user_id'],
            items=result['items']  # Simplified
        )
```

#### 4. Frameworks & Drivers (Outermost Layer)

**What:** External tools and frameworks (Web, Database, UI).

**Characteristics:**
- Most volatile, changes frequently
- No business logic
- Connects adapters to actual technologies

**Example:**
```python
# Frameworks & Drivers layer
from flask import Flask, request, jsonify

app = Flask(__name__)

# Wire dependencies (Dependency Injection)
database = PostgresDatabase('postgresql://...')
order_repository = PostgresOrderRepository(database)
payment_gateway = StripePaymentGateway(api_key='sk_test_...')

create_order_use_case = CreateOrderUseCase(order_repository, payment_gateway)
order_controller = OrderController(create_order_use_case)

# REST endpoint (framework-specific)
@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        response = order_controller.handle_create_order(request.json)
        return jsonify(response), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### The Dependency Rule

**Rule:** Source code dependencies must point inward.

```
Allowed:
Frameworks → Adapters → Use Cases → Entities ✓

NOT Allowed:
Entities → Use Cases ✗
Use Cases → Adapters ✗
Adapters → Frameworks ✗

Inner layers NEVER import from outer layers
```

**How to cross boundaries:**
```
Problem: Use Case needs to call Database, but can't depend on it (outer layer)

Solution: Dependency Inversion

Use Case defines interface (points inward):
class OrderRepository(Protocol):
    def save(self, order: Order): pass

Adapter implements interface (points inward to use case):
class PostgresOrderRepository:
    def save(self, order: Order):
        # Database code

Use Case:
def __init__(self, repo: OrderRepository):  # Depends on interface
    self.repo = repo

Dependency injection provides implementation:
repo = PostgresOrderRepository(database)
use_case = CreateOrderUseCase(repo)

Result: Dependency points inward (Adapter → Use Case), even though
        control flows outward (Use Case → Adapter)
```

### Clean Architecture Benefits

```
✓ Independent of frameworks
  ├── Business logic doesn't depend on Flask, Django, etc.
  ├── Can swap frameworks
  └── Test without framework

✓ Testable
  ├── Business rules testable without UI, DB, etc.
  ├── Fast unit tests
  └── Mock outer layers easily

✓ Independent of UI
  ├── Swap REST for GraphQL
  ├── Add mobile app
  └── CLI for same use cases

✓ Independent of database
  ├── Swap Postgres for MongoDB
  ├── Business logic unchanged
  └── No database in tests

✓ Independent of external agencies
  ├── Business rules don't know about Stripe, SendGrid
  ├── Easy to swap vendors
  └── Test without external calls
```

### Clean Architecture vs Hexagonal

**Similarities:**
- Both isolate business logic
- Both use dependency inversion
- Both define boundaries via interfaces

**Differences:**
```
Hexagonal:
├── Two-dimensional (inside/outside)
├── Ports and adapters terminology
└── Focus on pluggability

Clean:
├── Concentric circles (layers)
├── Entities, use cases, adapters, frameworks
└── Focus on dependency rule
```

Both are compatible and often used together!

---

## 4. Strangler Fig Pattern

### What is the Strangler Fig Pattern?

**Definition:** Incrementally migrate a legacy system by gradually replacing components with new implementations, eventually "strangling" the old system.

**Named after:** Strangler fig tree (grows around host tree, eventually replacing it)

**Key Idea:** Avoid "big bang" rewrites; migrate incrementally.

### The Problem: Legacy System Migration

```
Scenario: 10-year-old monolithic e-commerce system

Problems:
├── PHP codebase, poorly maintained
├── No tests
├── Tightly coupled
├── Business depends on it (can't shut down)
├── Full rewrite = 18 months, risky

Big Bang Rewrite Risks:
├── Business frozen for 18 months (no new features)
├── Existing bugs must be replicated (or customers complain)
├── Integration hell at end
├── Might not work when deployed
└── Historical example: Netscape 6.0 rewrite killed company
```

### The Strangler Fig Approach

```
Instead of:
[Old System] → [18 months] → [New System]

Do:
[Old System] → [Facade] → [Old System]
                   ↓
            [New Component 1] (month 1)
                   ↓
            [New Component 2] (month 2)
                   ↓
            [New Component 3] (month 3)
                   ...
            [Eventually: All new, retire old]

Incremental migration:
├── Start with new features
├── Migrate existing features one by one
├── Both systems run in parallel
└── Eventually, old system has zero traffic
```

### Implementation Strategy

#### Step 1: Create Facade/Proxy

**Place proxy in front of legacy system:**
```
Before:
Users → Legacy System

After:
Users → Proxy/Facade → Legacy System
```

**Example: API Gateway as Facade**
```nginx
# NGINX config (Proxy/Facade)

server {
    listen 80;

    # New user service (migrated)
    location /api/users {
        proxy_pass http://new-user-service:8080;
    }

    # New product service (migrated)
    location /api/products {
        proxy_pass http://new-product-service:8080;
    }

    # Everything else: Legacy system
    location / {
        proxy_pass http://legacy-php-app:80;
    }
}

# Users see one system, but requests routed to new or old
```

#### Step 2: Migrate Incrementally

**Choose migration order:**
```
Strategy 1: Start with new features
├── New features built as microservices
├── Don't touch legacy for new work
├── Legacy footprint doesn't grow
└── Example: New recommendation engine as separate service

Strategy 2: Migrate by business capability
├── Identify bounded contexts
├── Migrate least-coupled first
├── Example: User authentication → Product catalog → Orders
└── Each migration is small, testable

Strategy 3: Migrate by traffic
├── Migrate high-traffic endpoints first
├── Performance wins early
└── Example: Product search (1M requests/day) before admin panel (100 req/day)
```

**Example: Migrate User Service**
```
Phase 1: Create new User Service
├── Build new microservice (Node.js, Python, etc.)
├── Implement user registration, login
├── Use separate database
└── Deploy alongside legacy

Phase 2: Dual Writes
├── Write to both legacy and new database
├── Read from legacy (still source of truth)
└── Verify data consistency

Phase 3: Dual Reads
├── Read from new database
├── Compare with legacy (shadow traffic)
└── Log discrepancies

Phase 4: Cut Over
├── Update proxy to route to new service
├── Legacy user code no longer called
└── Monitor for issues

Phase 5: Cleanup
├── Remove user code from legacy
├── Migrate data fully
└── Decommission legacy user database
```

**Implementation:**
```python
# Phase 2: Dual writes
class UserService:
    def __init__(self, legacy_db, new_db):
        self.legacy = legacy_db
        self.new = new_db

    def create_user(self, username, email, password):
        # Write to legacy (source of truth for now)
        legacy_user = self.legacy.execute("""
            INSERT INTO users (username, email, password)
            VALUES (:username, :email, :password)
            RETURNING id
        """, {'username': username, 'email': email, 'password': hash_password(password)})

        # Also write to new system
        try:
            self.new.create_user({
                'legacy_id': legacy_user.id,
                'username': username,
                'email': email,
                'password_hash': hash_password(password)
            })
        except Exception as e:
            # Log but don't fail (new system not critical yet)
            logger.error(f"Failed to write to new user service: {e}")

        return legacy_user


# Phase 3: Dual reads with comparison
class UserService:
    def get_user(self, user_id):
        # Read from both
        legacy_user = self.legacy.query("SELECT * FROM users WHERE id = :id", {'id': user_id})
        new_user = self.new.get_user(user_id)

        # Compare
        if legacy_user and new_user:
            if legacy_user['email'] != new_user.email:
                logger.warning(f"Data mismatch for user {user_id}: {legacy_user['email']} vs {new_user.email}")

        # Return legacy (still source of truth)
        return legacy_user


# Phase 4: Cutover
class UserService:
    def get_user(self, user_id):
        # Read from new system only
        return self.new.get_user(user_id)
```

#### Step 3: Anti-Corruption Layer

**Problem:** New services shouldn't depend on legacy data models.

**Solution:** Translate between legacy and new models.

```python
# Legacy User Model
{
    'userid': 123,
    'uname': 'alice',
    'emailaddr': 'alice@example.com',
    'pwd_hash': '...',
    'created': '2010-01-15 10:30:00'
}

# New User Model
{
    'id': 123,
    'username': 'alice',
    'email': 'alice@example.com',
    'password_hash': '...',
    'created_at': '2010-01-15T10:30:00Z'
}

# Anti-Corruption Layer
class LegacyUserAdapter:
    """Translates between legacy and new models"""

    @staticmethod
    def to_new_model(legacy_user: dict) -> User:
        return User(
            id=legacy_user['userid'],
            username=legacy_user['uname'],
            email=legacy_user['emailaddr'],
            password_hash=legacy_user['pwd_hash'],
            created_at=datetime.strptime(legacy_user['created'], '%Y-%m-%d %H:%M:%S')
        )

    @staticmethod
    def to_legacy_model(user: User) -> dict:
        return {
            'userid': user.id,
            'uname': user.username,
            'emailaddr': user.email,
            'pwd_hash': user.password_hash,
            'created': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# New service uses clean model internally
# Adapter translates when interacting with legacy
```

### Strangler Fig Best Practices

```
✓ Start small
  ├── Pick lowest-risk component first
  ├── Prove the approach works
  └── Build confidence

✓ Measure and monitor
  ├── Track error rates
  ├── Compare performance (new vs old)
  ├── Monitor data consistency
  └── Have rollback plan

✓ Dual write, then dual read
  ├── Write to both systems first
  ├── Verify data consistency
  ├── Only then read from new system
  └── Gradual cutover reduces risk

✓ Feature flags
  ├── Route percentage of traffic to new system
  ├── Start with 1%, then 10%, then 100%
  ├── Quick rollback if issues
  └── Gradual validation

✓ Keep legacy running
  ├── Don't delete legacy code immediately
  ├── Keep it deployable (in case of rollback)
  └── Remove only when confident

✓ Anti-corruption layer
  ├── Protect new code from legacy models
  ├── Translate at boundary
  └── New code stays clean
```

### Real-World Example: Shopify

**Background:** PHP monolith handling millions of merchants

**Migration:**
```
2014: Started extracting services
├── Identity Service (authentication)
├── Product Service
├── Order Service

Strategy:
├── New features: Built as services
├── Existing features: Strangled incrementally
├── Proxy layer: Rails app routes to services
├── Each migration: 3-6 months

2024: Hundreds of services
├── Legacy still running (reduced footprint)
├── Core business logic in services
├── Incremental, never "big bang"
└── Zero downtime throughout
```

### When to Use Strangler Fig

```
Good fit:
✓ Large legacy system
✓ Cannot afford downtime
✓ Risk-averse organization
✓ Need to deliver features during migration
✓ Uncertain how to architect new system (learn as you go)

Not needed:
✗ Small system (rewrite is fast)
✗ Can afford downtime
✗ Legacy isn't critical
✗ Green field project
```

---

## Summary

### Comparing Patterns

```
Layered Architecture:
├── When: Simple to moderate complexity
├── Benefit: Easy to understand
├── Drawback: Coupling to database
└── Example: Traditional web apps

Hexagonal Architecture:
├── When: Complex business logic, multiple integrations
├── Benefit: Technology independent
├── Drawback: More abstraction
└── Example: Domain-rich applications

Clean Architecture:
├── When: Long-lived, evolving systems
├── Benefit: Independent of everything
├── Drawback: Highest complexity
└── Example: Enterprise applications

Strangler Fig:
├── When: Migrating legacy systems
├── Benefit: Incremental, low risk
├── Drawback: Dual-system complexity
└── Example: Monolith to microservices migration
```

### Choosing the Right Pattern

```
Simple CRUD app:
└── Layered Architecture ✓

Complex business rules:
└── Hexagonal or Clean Architecture ✓

Migrating legacy:
└── Strangler Fig ✓

Microservices:
└── Hexagonal (per service) + Strangler (migration) ✓

New greenfield project:
└── Start layered, evolve to hexagonal if needed ✓
```

---

## Further Reading

**Books:**
- "Clean Architecture" by Robert C. Martin
- "Implementing Domain-Driven Design" by Vaughn Vernon
- "Patterns of Enterprise Application Architecture" by Martin Fowler
- "Working Effectively with Legacy Code" by Michael Feathers

**Articles:**
- "Hexagonal Architecture" by Alistair Cockburn
- "The Clean Architecture" by Uncle Bob
- "Strangler Fig Application" by Martin Fowler

**Next Topics:**
- Domain-Driven Design (tactical patterns)
- Testing strategies for different architectures
- Dependency injection frameworks
- Migration case studies

---

**Remember:** Architecture patterns are tools, not rules. Choose based on your context: team skills, system complexity, business needs. Start simple, evolve as needed. Over-engineering is as harmful as under-engineering.
