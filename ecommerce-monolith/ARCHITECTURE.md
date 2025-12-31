# E-Commerce Monolith Architecture

## Overview
A traditional monolithic e-commerce platform built with FastAPI, React, and PostgreSQL. This application intentionally demonstrates common monolith patterns and limitations for educational purposes.

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT tokens
- **Validation:** Pydantic v2

### Frontend
- **Framework:** React 18+
- **State Management:** React Context / Redux (TBD)
- **HTTP Client:** Axios
- **Routing:** React Router
- **UI:** TailwindCSS (or Material-UI)

### Infrastructure
- **Database:** PostgreSQL (single instance)
- **Server:** Uvicorn
- **Development:** Docker Compose for local setup

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                      │
│                    (Single Page App)                    │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌─────────────────────────────────────────────────────────┐
│                FastAPI Monolith                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │             API Layer (Routers)                  │  │
│  │  /auth  /products  /cart  /orders  /payments    │  │
│  └────────────────────┬─────────────────────────────┘  │
│                       ▼                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Business Logic Layer                    │  │
│  │  UserService  ProductService  OrderService       │  │
│  │  PaymentService  NotificationService             │  │
│  └────────────────────┬─────────────────────────────┘  │
│                       ▼                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Data Access Layer                       │  │
│  │         SQLAlchemy Models & Queries              │  │
│  └────────────────────┬─────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────┘
                         ▼
              ┌──────────────────────┐
              │   PostgreSQL DB      │
              │  (Single Database)   │
              └──────────────────────┘
```

## Database Schema

### Tables

**users**
- id (PK)
- email (unique)
- password_hash
- full_name
- role (customer/admin)
- created_at
- updated_at

**products**
- id (PK)
- name
- description
- price
- category_id (FK)
- image_url
- created_at
- updated_at

**categories**
- id (PK)
- name
- description

**inventory**
- id (PK)
- product_id (FK) - TIGHTLY COUPLED
- quantity
- reserved_quantity
- updated_at

**carts**
- id (PK)
- user_id (FK)
- created_at
- updated_at

**cart_items**
- id (PK)
- cart_id (FK)
- product_id (FK)
- quantity
- price_snapshot

**orders**
- id (PK)
- user_id (FK)
- status (pending/paid/processing/shipped/delivered/cancelled)
- total_amount
- shipping_address
- created_at
- updated_at

**order_items**
- id (PK)
- order_id (FK)
- product_id (FK)
- quantity
- price_snapshot

**payments**
- id (PK)
- order_id (FK)
- amount
- status (pending/completed/failed)
- payment_method
- transaction_id
- created_at

**reviews**
- id (PK)
- product_id (FK)
- user_id (FK)
- rating (1-5)
- comment
- created_at

**notifications**
- id (PK)
- user_id (FK)
- type (order_confirmation/shipment/etc)
- message
- read
- created_at

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Products
- `GET /api/products` - List products (with pagination, filters)
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create product (admin only)
- `PUT /api/products/{id}` - Update product (admin only)
- `DELETE /api/products/{id}` - Delete product (admin only)

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category (admin only)

### Cart
- `GET /api/cart` - Get user's cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items/{id}` - Update cart item quantity
- `DELETE /api/cart/items/{id}` - Remove item from cart
- `DELETE /api/cart` - Clear cart

### Orders
- `POST /api/orders` - Create order (checkout)
- `GET /api/orders` - List user's orders
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}/status` - Update order status (admin)

### Payments
- `POST /api/payments/process` - Process payment
- `GET /api/payments/{id}` - Get payment status

### Reviews
- `GET /api/products/{id}/reviews` - Get product reviews
- `POST /api/products/{id}/reviews` - Create review
- `PUT /api/reviews/{id}` - Update review
- `DELETE /api/reviews/{id}` - Delete review

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/{id}/read` - Mark as read

## Intentional Monolith Pain Points

### 1. Tight Coupling - Order Creation Flow
When a user creates an order, the system performs these steps **synchronously in a single transaction**:

```python
# This all happens in one API call - BLOCKING!
def create_order(cart_id, user_id):
    # 1. Validate cart
    cart = get_cart(cart_id)

    # 2. Check inventory for ALL items (locks database rows)
    for item in cart.items:
        inventory = get_inventory(item.product_id)
        if inventory.available < item.quantity:
            raise OutOfStockError()

    # 3. Reserve inventory (updates multiple rows)
    for item in cart.items:
        reserve_inventory(item.product_id, item.quantity)

    # 4. Create order record
    order = create_order_record(cart, user_id)

    # 5. Process payment (external API call - SLOW!)
    payment = process_payment(order.total)

    # 6. Update order status
    order.status = "paid"

    # 7. Reduce inventory
    for item in cart.items:
        reduce_inventory(item.product_id, item.quantity)

    # 8. Send email notification (BLOCKS the response!)
    send_order_confirmation_email(user_id, order)

    # 9. Create notification record
    create_notification(user_id, f"Order {order.id} confirmed")

    # 10. Clear cart
    clear_cart(cart_id)

    # Finally return - user waited for ALL of this!
    return order
```

**Pain Points:**
- User waits 3-5 seconds for response (email sending is slow!)
- If email service is down, entire order creation fails
- Database transaction locks multiple tables
- No retry mechanism if payment fails midway
- All-or-nothing: entire flow must succeed

### 2. Shared Database - Complex Joins
Product listing with reviews needs expensive joins:

```sql
SELECT p.*, c.name as category_name,
       AVG(r.rating) as avg_rating,
       COUNT(r.id) as review_count,
       i.quantity as stock
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN reviews r ON p.id = r.product_id
LEFT JOIN inventory i ON p.id = i.product_id
GROUP BY p.id, c.name, i.quantity
```

**Pain Points:**
- Slow queries as data grows
- One slow query affects entire application
- Index optimization helps one query but hurts another
- Database becomes bottleneck

### 3. No Service Boundaries
Everything accesses everything:

```python
# OrderService directly imports and uses:
from services.inventory import InventoryService
from services.payment import PaymentService
from services.notification import NotificationService
from services.user import UserService

# Circular dependencies nightmare!
# Can't deploy/update one without affecting all
```

### 4. Single Deployment Unit
```yaml
# Everything deploys together
# Bug in review feature? Redeploy EVERYTHING
# Want to scale payments? Scale EVERYTHING (wasteful)
```

### 5. Technology Lock-in
- All code must use Python/FastAPI
- Can't use specialized tools (e.g., Elasticsearch for search)
- Can't use different databases for different needs

### 6. Scalability Limitations
- Can only scale vertically (bigger server) or
- Horizontal scaling requires session stickiness
- Database becomes bottleneck quickly
- High memory usage (everything loaded)

## Development Workflow

### Local Setup
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start FastAPI
uvicorn main:app --reload

# In another terminal - start frontend
cd frontend
npm install
npm start
```

### Project Structure
```
ecommerce-monolith/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/          # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── ...
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   └── ...
│   │   ├── services/        # Business logic
│   │   │   ├── user_service.py
│   │   │   ├── order_service.py
│   │   │   ├── payment_service.py
│   │   │   └── ...
│   │   └── utils/
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── context/
│   │   └── App.jsx
│   ├── package.json
│   └── .env
├── docker-compose.yml
└── README.md
```

## What We'll Learn From This

By building and using this monolith, you'll experience:

1. **Tight Coupling Issues** - Changing one feature affects others
2. **Performance Problems** - Slow queries, blocking operations
3. **Deployment Challenges** - Small change requires full redeployment
4. **Scaling Difficulties** - Can't scale individual components
5. **Development Friction** - Large codebase, hard to navigate
6. **Database Bottlenecks** - Single point of failure

These pain points will make the distributed architecture patterns in Phase 2+ much more meaningful!

## Next Steps

1. Set up project structure
2. Implement database models
3. Build core API endpoints
4. Create basic React UI
5. **Document pain points as we hit them**
6. Use this as baseline for decomposition in Phase 2

---

**Note:** This is intentionally NOT best-practice architecture. We're building a learning tool that demonstrates why we need distributed systems.
