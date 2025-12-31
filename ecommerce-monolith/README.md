# E-Commerce Monolith

A traditional monolithic e-commerce application built for learning system design principles. This application intentionally demonstrates common monolith patterns, limitations, and pain points.

## Purpose

This is a **learning project** designed to:
1. Experience real monolith limitations firsthand
2. Provide a baseline for understanding distributed architecture benefits
3. Serve as a reference for decomposition into microservices

**This is NOT production-ready code.** It intentionally includes anti-patterns for educational purposes.

## Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** React 18+
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

## Quick Start

### 1. Clone and Setup

```bash
cd ecommerce-monolith
```

### 2. Start Infrastructure (PostgreSQL + MailHog)

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- MailHog (email testing) on ports 1025 (SMTP) and 8025 (Web UI)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the application
python -m app.main
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 4. Frontend Setup (Coming Soon)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

## Project Structure

```
ecommerce-monolith/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User and auth models
│   │   │   ├── product.py       # Product, Category, Inventory
│   │   │   ├── cart.py          # Shopping cart models
│   │   │   ├── order.py         # Order and payment models
│   │   │   └── ...
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── routers/             # API endpoint routes
│   │   ├── services/            # Business logic layer
│   │   └── utils/               # Helper utilities
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── ...
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Key Features

- **User Management:** Registration, authentication, roles (customer/admin)
- **Product Catalog:** Products, categories, inventory management
- **Shopping Cart:** Add/remove items, persist cart
- **Order Management:** Checkout, order history, status tracking
- **Payment Processing:** Simulated payment gateway (with intentional delays)
- **Notifications:** Email notifications (synchronous, blocking)
- **Reviews & Ratings:** Product reviews

## Intentional Pain Points

This monolith includes these anti-patterns on purpose:

### 1. Tight Coupling
- Order creation synchronously calls inventory, payment, and email services
- All services share the same database models
- Direct imports between all modules

### 2. Blocking Operations
- Email sending is synchronous (2-second delay)
- Payment processing is synchronous (1-second delay)
- User waits for ALL operations to complete

### 3. Single Database
- One PostgreSQL database for everything
- Complex joins across multiple tables
- Database becomes bottleneck

### 4. No Service Boundaries
- Everything can access everything
- Hard to understand blast radius of changes
- Difficult to test in isolation

### 5. Single Deployment Unit
- Must deploy entire application for any change
- Can't scale individual components
- All-or-nothing releases

## Development Tools

### MailHog (Email Testing)
View sent emails at: http://localhost:8025

### Database Management
Connect to PostgreSQL:
```bash
docker exec -it ecommerce-postgres psql -U ecommerce -d ecommerce_db
```

Or use pgAdmin:
```bash
docker-compose --profile tools up
```
Access at: http://localhost:5050

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the Pain Points

### Experience Blocking Operations
```bash
# Create an order - notice the 3-5 second delay
# This is intentional to demonstrate blocking behavior
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"cart_id": 1}'
```

### Watch Email Delay
Check the terminal logs to see email sending blocking the response.

### Monitor Database Load
```sql
-- See active queries
SELECT * FROM pg_stat_activity;
```

## What You'll Learn

By building and using this monolith, you'll experience:

1. **Performance Degradation** - As data grows, complex joins slow down
2. **Deployment Risk** - Small changes require full redeployment
3. **Scaling Challenges** - Can't scale payment processing independently
4. **Coupling Issues** - Email service down = orders can't be created
5. **Development Friction** - Hard to work on features independently

## Next Steps in Learning Journey

Once you've built and experienced this monolith:

1. **Phase 1 (Current):** Document the specific pain points you encounter
2. **Phase 2:** Design microservices decomposition strategy
3. **Phase 3:** Implement caching and load balancing
4. **Phase 4:** Separate databases (polyglot persistence)
5. **Phase 5+:** Continue through the learning phases in `../claude.md`

## Contributing

This is a learning project. Feel free to:
- Add more features
- Intentionally make it worse (for learning!)
- Document additional pain points
- Share insights

## License

MIT License - This is for educational purposes

## Related Documentation

- See `../ARCHITECTURE.md` for detailed system design
- See `../claude.md` for the complete learning curriculum
- See `../PROGRESS.md` for your learning progress
