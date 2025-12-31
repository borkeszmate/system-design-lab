# System Design Learning - Progress Tracker

## Quick Resume (For New Sessions)
**Current Phase:** Phase 2+ - Production-Ready Microservices with Best Practices (COMPLETE!)
**Current Focus:** Clean architecture, database-per-service pattern, industry best practices
**Last Updated:** 2025-12-26 (Session 5 Complete!)
**Status:** ✅ Phase 1 Complete (Monolith) | ✅ Phase 2 Complete (Microservices) | ✅ Phase 2+ Complete (Best Practices) | 🎯 <500ms response vs 7600ms monolith (15x faster!) | 🏗️ Production-ready architecture | 🚀 Ready for Phase 3: Advanced topics!

---

## Session History

### Session 1 - 2025-12-19
**Goals:**
- Set up learning journey structure
- Begin Phase 1: Foundation
- Start building e-commerce monolith as reference application

**Completed:**
- ✅ Created claude.md with complete 10-phase learning curriculum
- ✅ Created PROGRESS.md for session tracking
- ✅ Decided on e-commerce platform as reference monolith
- ✅ Chose tech stack: FastAPI + React + PostgreSQL
- ✅ Designed monolith architecture with intentional pain points
- ✅ Created ARCHITECTURE.md with complete system design
- ✅ Created complete project structure (backend + frontend)
- ✅ Set up Docker Compose (PostgreSQL + MailHog)
- ✅ Created backend configuration files (config, database, main)
- ✅ Created sample models (User, Product, Category, Inventory)
- ✅ Set up React frontend with Vite
- ✅ Created README.md with setup instructions
- ✅ Set up Poetry for backend dependency management
- ✅ Started PostgreSQL and MailHog containers
- ✅ Started backend server on http://localhost:8000
- ✅ Started frontend development server on http://localhost:3000
- ✅ Verified all services are running and healthy

**Current State:**
- 🎉 Full stack is RUNNING and ready for development!
- Backend API: http://localhost:8000 (docs at /docs)
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- MailHog UI: http://localhost:8025

**Next Steps:**
1. Complete all database models (Cart, Order, Payment, Review, Notification)
2. Implement Pydantic schemas for validation
3. Build authentication system (JWT)
4. Create API routers and services
5. Implement the intentional pain points (blocking operations)
6. Test and document the monolith limitations
7. Build basic frontend UI components

**Decisions Made:**
- Using e-commerce platform as primary learning vehicle
- Building a real monolith first, then decomposing it in later phases
- Two-file tracking system (claude.md + PROGRESS.md)
- Tech stack: FastAPI (backend), React (frontend), PostgreSQL (database)
- Intentionally building in coupling, blocking operations, and single database for learning
- 7 core features: Users, Products, Cart, Orders, Payments, Notifications, Reviews

**Notes & Insights:**
- Starting with concrete code rather than theory for better learning
- Will intentionally build in common monolith limitations for educational purposes

### Session 1 (continued) - 2025-12-19
**Goals:**
- Complete database models with tight coupling
- Create Pydantic schemas for all entities
- Prepare for authentication and service implementation

**Completed:**
- ✅ Created Cart and CartItem models
- ✅ Created Order, OrderItem, and Payment models
- ✅ Created Review and Notification models
- ✅ All 11 database tables created in PostgreSQL
- ✅ Verified foreign key relationships and constraints
- ✅ Created complete Pydantic schemas for all entities:
  - User and Auth schemas (login, registration, tokens)
  - Product and Category schemas
  - Cart schemas
  - Order and Payment schemas
  - Review and Notification schemas
- ✅ Created HOW_TO_RESUME.md with resume instructions

**Current State:**
- Backend auto-reloaded with new models
- Database schema fully implemented with tight coupling
- Ready for authentication and service layer implementation

**Next Steps:**
1. Build JWT authentication system (utils/auth.py)
2. Create service layer with intentional blocking operations:
   - OrderService with synchronous email and payment
   - EmailService with artificial delay (2 seconds)
   - PaymentService with artificial delay (1 second)
3. Implement API routers
4. Test the monolith pain points
5. Document limitations experienced

**Key Learning Points:**
- Database design shows tight coupling: Order references User, OrderItems, Payment
- All relationships use foreign keys - hard to split into separate services
- Single database = single point of failure and bottleneck
- This coupling is intentional for learning purposes!

### Session 1 (Final) - 2025-12-19
**Goals:**
- Complete authentication system
- Implement blocking services (email, payment)
- Create the nightmare order service
- Build all API routers
- Test the monolith pain points

**Completed:**
- ✅ JWT authentication system with password hashing
- ✅ EmailService with intentional 2-second blocking delay
- ✅ PaymentService with intentional 1-second blocking delay
- ✅ OrderService with 11 synchronous steps (3-5 second total blocking!)
- ✅ Authentication router (register, login, /me)
- ✅ Products router (CRUD with admin auth)
- ✅ Cart router (add/remove items, view cart)
- ✅ Orders router with THE SLOW CHECKOUT endpoint 🐌
- ✅ 13 total API endpoints
- ✅ Complete Swagger UI documentation
- ✅ Created comprehensive testing guide (TESTING_THE_PAIN.md)
- ✅ Created session summary (SESSION_SUMMARY.md)

**What We Built:**
- **~2000+ lines of code**
- **11 database tables** with tight coupling
- **5 service modules** (email, payment, order + auth utilities)
- **4 API routers** with 13 endpoints
- **Complete authentication** with JWT
- **Intentional anti-patterns** for learning

**The Star Feature:**
`POST /api/orders/checkout` - Takes 3-5 seconds!
- Step 6: Payment processing (1s delay) 💀
- Step 9: Email sending (2s delay) 💀💀
- Total: 3-5 seconds of blocking operations
- User waits for EVERYTHING!

**Next Steps:**
1. Test the checkout endpoint to experience the pain
2. Document what you learned
3. Begin Phase 2: Microservices decomposition
4. Compare monolith vs. microservices performance

**Session Duration:** ~2 hours
**Status:** ✅ MONOLITH COMPLETE AND FUNCTIONAL!

### Session 2 - 2025-12-20
**Goals:**
- Test the monolith pain points
- Experience the 3-5 second checkout delay
- Demonstrate database locking and concurrent blocking
- Document observations and learnings

**Completed:**
- ✅ Fixed bcrypt compatibility issue (downgraded from 5.0.0 to 4.0.1)
- ✅ Restarted Docker containers and backend after 1-day break
- ✅ Registered test users (paintest@example.com, user2@test.com)
- ✅ Created category: Electronics
- ✅ Created product: Gaming Laptop ($1299.99)
- ✅ Added items to cart for multiple users
- ✅ **EXPERIENCED THE PAIN:** 7.63 second checkout! (worse than expected 3-5s)
- ✅ Demonstrated PostgreSQL row-level locks (`SELECT ... FOR UPDATE`)
- ✅ Showed concurrent blocking: User 2 blocked by User 1's inventory lock
- ✅ Verified email sent to MailHog (order confirmation)
- ✅ Documented all 11 synchronous steps in OrderService

**What We Observed:**
1. **Blocking Operations:**
   - Payment processing: 1 second delay
   - Email sending: 2 seconds delay
   - Database operations: ~4.6 seconds overhead
   - **Total: 7.63 seconds** (user waited for EVERYTHING)

2. **Database Locking:**
   - `RowExclusiveLock` held on inventory table for 7+ seconds
   - Lock acquired at Step 3 (Reserve Inventory)
   - Lock held through payment, email, and all operations
   - Lock released only at transaction COMMIT

3. **Concurrent User Impact:**
   - Two users trying to buy the same product
   - User 1: Gets lock, completes in 7.6s
   - User 2: BLOCKED waiting for User 1's lock
   - Demonstrated serialization instead of parallelization

4. **Real-World Implications:**
   - Black Friday scenario: 100 users = 700 seconds (11.6 minutes!)
   - Cannot scale individual services (email, payment)
   - Email failure = entire order rollback
   - No retry mechanism or graceful degradation

**Backend Logs Analysis:**
```
================================================================================
🛒 [OrderService] Starting order creation...
⚠️  [MONOLITH ALERT] This will BLOCK for 3-5 seconds!
================================================================================
[Step 1/11] Getting user's cart...
[Step 2/11] Validating cart items and checking inventory...
[Step 3/11] Reserving inventory (locking database rows)...
    SQL: SELECT ... FROM inventory WHERE product_id = 1 FOR UPDATE
    🔒 LOCK ACQUIRED
[Step 4/11] Creating order record...
[Step 5/11] Creating order items...
[Step 6/11] Processing payment...
    💀 BLOCKING OPERATION - Payment gateway call
    ⏳ [PaymentService] Calling payment gateway... (1s delay)
[Step 7/11] Recording payment...
[Step 8/11] Reducing inventory...
[Step 9/11] Sending confirmation email...
    💀💀 BLOCKING OPERATION - Email sending
    ⏳ [EmailService] This will take 2 seconds...
[Step 10/11] Creating notification...
[Step 11/11] Clearing cart...
    🔒 LOCK RELEASED (COMMIT)
================================================================================
⏱️  Total response time: 7.63 seconds
😢 User had to wait 7.63 seconds for their order!
================================================================================
```

**Key Learnings:**
1. **Why Monoliths Don't Scale:**
   - Single database transaction = single point of contention
   - Row-level locks prevent concurrent processing
   - Synchronous operations block the entire request
   - Cannot scale services independently

2. **What Microservices Would Fix:**
   - Order service returns immediately (<500ms)
   - Payment processed asynchronously via message queue
   - Email sent asynchronously (user doesn't wait)
   - Inventory updated via events
   - No long-held locks
   - Independent scaling of each service

3. **Database Lock Types Observed:**
   - `RowExclusiveLock`: Main lock from FOR UPDATE
   - `RowShareLock`: For reading the row
   - `AccessShareLock`: General table access

**Tools Used:**
- PostgreSQL `pg_locks` system catalog
- PostgreSQL `pg_stat_activity` monitoring
- curl for API testing
- MailHog for email verification
- Custom lock monitoring scripts

**Session Duration:** ~1 hour
**Status:** ✅ PHASE 1 COMPLETE! Pain points thoroughly experienced and documented.

**Next Steps:**
1. Begin Phase 2: Microservices Decomposition
2. Design microservices architecture
3. Implement async order processing with message queues
4. Compare performance: Monolith (7.6s) vs Microservices (<500ms)
5. Demonstrate independent scaling

### Session 3 - 2025-12-20 (Later)
**Goals:**
- Add duration tracking to orders
- Build frontend to visualize the pain
- Create complete user flow with timer

**Completed:**
- ✅ Added `processing_duration_ms` field to Order model
- ✅ Updated OrderService to track checkout timing (milliseconds)
- ✅ Created database migration: `ALTER TABLE orders ADD COLUMN processing_duration_ms`
- ✅ Updated Pydantic schemas to include duration in API response
- ✅ Built complete React frontend with:
  - Product catalog display
  - Shopping cart functionality
  - **Live timer during checkout** (updates every 100ms)
  - Order confirmation showing exact duration
  - Visual pain indicators (spinner, pulsing alert, timer)
- ✅ Styled frontend with gradient themes and responsive design
- ✅ Tested complete flow: Login → Add to cart → Checkout → See duration

**What the Frontend Shows:**
1. **During Checkout:**
   - Live timer: "Checking out... 5.2s"
   - Spinning loader animation
   - Pulsing alert box with pain message
   - Real-time elapsed time counter

2. **After Checkout:**
   - Order confirmation banner (green gradient)
   - Order ID and total amount
   - **Processing Duration** in large red text
   - Breakdown: "You waited X seconds for payment (1s) + email (2s) + DB ops"
   - Promise: "With microservices, this would take <500ms"

**Technical Implementation:**
```javascript
// Frontend timer starts before API call
const startTime = Date.now()
const timerInterval = setInterval(() => {
  setCheckoutTimer(Date.now() - startTime)
}, 100)

// Backend tracks server-side duration
start_time = time.time()
// ... process order ...
duration_ms = int((time.time() - start_time) * 1000)
order.processing_duration_ms = duration_ms
```

**Duration Data Now Available:**
- Stored in database: `orders.processing_duration_ms`
- Returned in API: `OrderResponse.processing_duration_ms`
- Displayed in UI: Large red timer showing exact wait time
- Query: `SELECT id, processing_duration_ms FROM orders;`

**User Experience Captured:**
- ⏰ User sees live timer ticking up
- 😫 Can't browse, can't cancel, must wait
- ⏱️ Final duration: ~7000-8000ms displayed prominently
- 💡 Comparison with microservices promise (<500ms)

**Files Created/Modified:**
- `backend/app/models/order.py` - Added duration field
- `backend/app/schemas/order.py` - Added to response
- `backend/app/services/order_service.py` - Added timing logic
- `frontend/src/App.jsx` - Complete new UI with timer
- `frontend/src/App.css` - Full styling with animations
- Database: Added column to orders table

**Session Duration:** ~30 minutes
**Status:** ✅ PHASE 1 FULLY COMPLETE WITH DEMO UI!

**Ready to Demo:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Complete flow with visual timer
- Duration saved to database for comparison with Phase 2

### Session 4 - 2025-12-21
**Goals:**
- Begin Phase 2: Microservices Architecture
- Decompose monolith into independent services
- Implement async processing with message queues
- Achieve <500ms response time

**Completed:**
- ✅ Created complete microservices architecture with 5 services
- ✅ **API Gateway** (Port 9000) - Single entry point
- ✅ **Order Service** (Port 8001) - Order creation with PostgreSQL (5433)
- ✅ **Payment Service** (Port 8002) - Async payment processing with PostgreSQL (5434)
- ✅ **Email Service** (Port 8003) - Async email sending (stateless)
- ✅ RabbitMQ message broker (Port 5672, Management: 15672)
- ✅ MailHog for email testing (Port 8026)
- ✅ Docker Compose orchestration with 9 containers
- ✅ Event-driven architecture with topic exchange
- ✅ Database-per-service pattern (2 separate PostgreSQL instances)

**Architecture Patterns Implemented:**
- **Event-Driven Architecture**: RabbitMQ with topic exchange
- **Database-per-Service**: Order DB (5433) and Payment DB (5434)
- **API Gateway Pattern**: Single entry point at port 9000
- **Async Processing**: Background workers consuming events
- **Message Routing**:
  - `order.order.created` → Payment Service
  - `payment.payment.processed` → Email Service

**Performance Achievement:**
| Metric | Monolith | Microservices | Improvement |
|--------|----------|---------------|-------------|
| Response Time | 7,600ms | **13ms** | **583x faster!** |
| Payment | Blocking 1s | Async background | User doesn't wait |
| Email | Blocking 2s | Async background | User doesn't wait |

**Event Flow:**
1. Client → API Gateway: POST /api/checkout
2. Order Service: Creates order (13ms), publishes `OrderCreated` event
3. API Gateway → Client: **Immediate response!**
4. Payment Service: Consumes event, processes payment (1s), publishes `PaymentProcessed`
5. Email Service: Consumes event, sends email (2s)

**Technical Details:**
- 6 Docker containers running simultaneously
- Pika library for RabbitMQ integration
- SQLAlchemy with separate database connections
- FastAPI for all HTTP services
- Topic exchange with routing keys
- Durable queues for reliability

**Testing Verified:**
- ✅ Order creation: 13ms response
- ✅ Payment processing: Async in background
- ✅ Email delivery: Visible in MailHog
- ✅ RabbitMQ Management UI: Events flowing correctly
- ✅ Database isolation: Each service owns its data

**Session Duration:** ~2 hours
**Status:** ✅ PHASE 2 COMPLETE! Microservices working with 583x performance improvement!

**Key Learnings:**
- Message queues enable true async processing
- Database-per-service provides isolation and independent scaling
- Event-driven architecture decouples services
- Users don't wait for background operations
- 583x faster response = dramatically better UX

### Session 5 - 2025-12-26
**Goals:**
- Apply industry best practices to microservices
- Implement clean architecture pattern
- Create production-ready folder structure
- Add proper state management to frontend
- Build real microservices with actual databases (no mocking)

**Completed:**
- ✅ Created 3 new production-ready microservices:
  - **Product Service** (Port 8004, PostgreSQL 5435) - Clean architecture example
  - **User Service** (Port 8005, PostgreSQL 5436) - JWT auth with bcrypt
  - **Cart Service** (Port 8006, PostgreSQL 5437) - Service-to-service communication
- ✅ Implemented **Clean Architecture** in Product Service:
  - `api/` - HTTP routes and dependencies (API layer)
  - `core/` - Business logic and services (Core layer)
  - `domain/` - Models and schemas (Domain layer)
  - `infrastructure/` - Database and repositories (Infrastructure layer)
- ✅ Built professional React frontend with Redux Toolkit
- ✅ **Reorganized folder structure** following best practices:
  - All microservices moved to `services/` folder
  - Shared utilities in `shared/` (events, logging)
  - Infrastructure as Code folders prepared
  - Documentation structure created
- ✅ Updated all Docker Compose paths and rebuilt services
- ✅ Auto-seeded databases with test data
- ✅ Created comprehensive documentation (ARCHITECTURE.md)

**Architecture Patterns Added:**
1. **Clean Architecture** - 4-layer design (API, Core, Domain, Infrastructure)
2. **Repository Pattern** - Abstract data access from business logic
3. **Service Layer Pattern** - Business logic separated from API handlers
4. **Dependency Injection** - FastAPI's DI system throughout
5. **Database-per-Service** - 5 isolated PostgreSQL databases total
6. **API Gateway Pattern** - Refactored to route to real services (no mocking)

**Folder Structure (Best Practices):**
```
ecommerce-microservices/
├── api-gateway/           # Single entry point
├── services/              # All microservices
│   ├── product-service/  # Clean architecture reference
│   ├── user-service/
│   ├── cart-service/
│   ├── order-service/
│   ├── payment-service/
│   └── email-service/
├── frontend/              # React + Redux
├── shared/                # Shared utilities (events, logging)
├── infrastructure/        # IaC (docker, k8s, terraform)
├── scripts/               # Automation (setup.sh)
└── docs/                  # Documentation
```

**Frontend Features (React + Redux Toolkit):**
- Redux slices: auth, products, cart, orders
- API service layer with retry logic (exponential backoff)
- Real-time order status polling (every 2s)
- Error boundaries for graceful error handling
- Similar design to monolith for comparison

**System Scale:**
- **15 containers** running simultaneously
- **6 microservices** (Product, User, Cart, Order, Payment, Email)
- **5 PostgreSQL databases** (fully isolated)
- **1 API Gateway**
- **1 Frontend**
- **1 RabbitMQ**
- **1 MailHog**

**Performance Comparison:**
| Metric | Monolith | Microservices | Improvement |
|--------|----------|---------------|-------------|
| Checkout Time | 7,600ms | <500ms | **15x faster** |
| User Wait | 7.6s | 0.5s | **93% reduction** |
| Processing | Synchronous | Asynchronous | Non-blocking |
| Databases | 1 shared | 5 isolated | Full isolation |
| Scalability | Scale all | Per service | Granular control |

**Documentation Created:**
- `ARCHITECTURE.md` - Complete architecture patterns and principles
- `SESSION_5_SUMMARY.md` - Detailed session summary
- `CURRENT_STATE.md` - System overview and quick start
- `product-service/README.md` - Clean architecture example
- `.env.example` files - Environment templates for each service

**Supporting Infrastructure:**
- Test structure (unit, integration, fixtures) for all services
- Shared event schemas (RabbitMQ message formats)
- Shared logging utility (consistent across services)
- Setup automation script (scripts/setup.sh)

**Session Duration:** ~3 hours
**Status:** ✅ PHASE 2+ COMPLETE! Production-ready microservices with industry best practices!

**Key Learnings:**
- Clean architecture makes services testable and maintainable
- Repository pattern abstracts data access for flexibility
- Service layer separates business logic from API concerns
- Database-per-service enables true service autonomy
- Proper folder structure improves codebase navigation
- Redux Toolkit significantly reduces boilerplate
- Service-to-service communication (Cart → Product Service)

**URLs:**
- Frontend: http://localhost:3000
- API Gateway: http://localhost:9000
- Product Service: http://localhost:8004
- User Service: http://localhost:8005
- Cart Service: http://localhost:8006
- Order Service: http://localhost:8001
- Payment Service: http://localhost:8002
- Email Service: http://localhost:8003
- RabbitMQ UI: http://localhost:15672
- MailHog UI: http://localhost:8026

---

## Overall Progress

### Phases Completed: 2/10
- [x] Phase 1: Foundation (COMPLETE - Monolith built and tested!)
- [x] Phase 2: Architecture Patterns (COMPLETE - Microservices with clean architecture!)
- [ ] Phase 3: Scalability & Performance
- [ ] Phase 4: Data Management
- [ ] Phase 5: Reliability & Resilience
- [ ] Phase 6: Observability & Monitoring
- [ ] Phase 7: Security & Identity
- [ ] Phase 8: Deployment & DevOps
- [ ] Phase 9: Real-World Systems
- [ ] Phase 10: Advanced Topics

### Mini Projects: 0/5
- [ ] URL Shortener
- [ ] Task Queue System
- [ ] Chat Application
- [ ] Rate Limiter
- [ ] Notification Service

### Capstone Project: Not Started
- [ ] Design document
- [ ] Implementation
- [ ] Testing & optimization
- [ ] Documentation

---

## Built Artifacts

### Applications

#### 1. E-commerce Monolith - ✅ COMPLETE
- **Purpose:** Reference application demonstrating monolith limitations
- **Status:** Fully functional with frontend UI and duration tracking
- **Location:** `ecommerce-monolith/`
- **Stack:** FastAPI + React + PostgreSQL + MailHog
- **Features:**
  - ✅ User authentication (JWT)
  - ✅ Product catalog
  - ✅ Shopping cart
  - ✅ **Slow checkout with 7.6s delay** (intentional pain point)
  - ✅ Payment processing (1s blocking delay)
  - ✅ Email sending (2s blocking delay)
  - ✅ Order management
  - ✅ Duration tracking (saved to DB)
  - ✅ Frontend with live timer
- **URLs:**
  - Frontend: http://localhost:3000
  - Backend API: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - MailHog: http://localhost:8025

#### 2. E-commerce Microservices - ✅ COMPLETE
- **Purpose:** Production-ready microservices demonstrating best practices
- **Status:** Fully functional with clean architecture and 15 containers
- **Location:** `ecommerce-microservices/`
- **Stack:** FastAPI + React + Redux + PostgreSQL (x5) + RabbitMQ
- **Architecture:**
  - 6 microservices (Product, User, Cart, Order, Payment, Email)
  - 5 isolated PostgreSQL databases (database-per-service)
  - 1 API Gateway (single entry point)
  - 1 RabbitMQ message broker (async events)
  - 1 React + Redux frontend
  - Clean Architecture pattern (Product Service as reference)
- **Features:**
  - ✅ **<500ms checkout response** (15x faster than monolith!)
  - ✅ Async payment and email processing
  - ✅ Event-driven architecture (RabbitMQ)
  - ✅ Database-per-service pattern
  - ✅ Repository pattern (data access abstraction)
  - ✅ Service layer pattern (business logic)
  - ✅ Dependency injection (FastAPI DI)
  - ✅ JWT authentication with bcrypt
  - ✅ Service-to-service communication (Cart → Product)
  - ✅ Redux Toolkit state management
  - ✅ Real-time order status polling
  - ✅ Error boundaries and retry logic
  - ✅ Shared utilities (events, logging)
- **URLs:**
  - Frontend: http://localhost:3000
  - API Gateway: http://localhost:9000
  - Product Service: http://localhost:8004
  - User Service: http://localhost:8005
  - Cart Service: http://localhost:8006
  - Order Service: http://localhost:8001
  - Payment Service: http://localhost:8002
  - Email Service: http://localhost:8003
  - RabbitMQ UI: http://localhost:15672
  - MailHog UI: http://localhost:8026

### Documentation
- `CLAUDE.md` - Learning curriculum and roadmap (10 phases)
- `PROGRESS.md` - This file, session tracking
- `ecommerce-monolith/ARCHITECTURE.md` - Monolith architecture and design
- `ecommerce-monolith/README.md` - Monolith setup and usage guide
- `ecommerce-microservices/ARCHITECTURE.md` - Microservices architecture patterns
- `ecommerce-microservices/CURRENT_STATE.md` - System overview and quick start
- `ecommerce-microservices/SESSION_4_SUMMARY.md` - Session 4 summary
- `ecommerce-microservices/SESSION_5_SUMMARY.md` - Session 5 summary
- `ecommerce-microservices/services/product-service/README.md` - Clean architecture example

### Code Structure
- `ecommerce-monolith/backend/` - FastAPI backend
  - **Configuration:** config.py, database.py, main.py
  - **Models (11 tables):** User, Product, Category, Inventory, Cart, CartItem, Order, OrderItem, Payment, Review, Notification
  - **Schemas:** Complete Pydantic validation for all models
  - **Routers (4):** auth.py, products.py, cart.py, orders.py (13 endpoints total)
  - **Services (3):** email_service.py (2s delay), payment_service.py (1s delay), order_service.py (11 steps)
  - **Utils:** auth.py (JWT + bcrypt)
  - **Docker:** docker-compose.yml (PostgreSQL + MailHog)
  - **Dependencies:** Poetry with bcrypt 4.0.1 (downgraded for compatibility)

- `ecommerce-monolith/frontend/` - React + Vite frontend
  - **App.jsx:** Complete UI with product catalog, cart, checkout with live timer
  - **App.css:** Full styling with gradients, animations, responsive design
  - **Features:**
    - Product listing and "Add to Cart"
    - Shopping cart with total
    - Checkout button with live timer (updates every 100ms)
    - Order confirmation with processing duration display
    - Visual pain indicators (spinner, pulsing alerts)
  - **Vite config:** Proxy to backend at port 8000

---

## Key Learnings

### Phase 1: Foundation - Monolith Limitations

**Database Locking:**
- `SELECT ... FOR UPDATE` creates row-level locks that block concurrent transactions
- Locks held for entire transaction duration (7+ seconds in our case)
- `RowExclusiveLock`: Prevents other transactions from reading with FOR UPDATE
- Real-world impact: Black Friday with 100 users = 11.6 minutes wait time for last user

**Synchronous Operations:**
- Payment gateway: 1s blocking delay
- Email sending: 2s blocking delay
- Total checkout time: 7.63 seconds (user waits for EVERYTHING)
- No way to continue browsing or cancel during checkout

**Tight Coupling:**
- Email failure = entire order rollback
- Cannot scale email service independently
- Cannot retry failed operations without redoing everything
- Single database = single point of failure

**Monolith vs Microservices Performance:**
- Monolith: 7.63s synchronous response
- Microservices (future): <500ms response, background processing
- Key difference: User doesn't wait for email/payment in microservices

**PostgreSQL Lock Monitoring:**
- `pg_locks` system catalog shows active locks
- `pg_stat_activity` shows transaction state and duration
- Locks persist until COMMIT or ROLLBACK
- Multiple lock types: RowExclusiveLock, RowShareLock, AccessShareLock

**Why This Matters:**
- Demonstrates real-world scalability problems
- Shows why distributed systems need async patterns
- Proves the need for message queues and event-driven architecture
- Explains why microservices exist (not just hype!)

**Duration Tracking & Visualization:**
- Added `processing_duration_ms` column to orders table
- Backend tracks exact server-side processing time (Python `time.time()`)
- Frontend shows live timer during checkout (JavaScript `Date.now()`)
- Duration saved to database for historical comparison
- Visual feedback: Spinning loader, pulsing alert, live counter
- Order confirmation displays duration prominently in red
- Enables data-driven comparison: Monolith vs Microservices

**Frontend UX Learnings:**
- Live timer makes the pain visceral and real
- User can't cancel, can't browse - stuck waiting
- Visual countdown creates anxiety and frustration
- Comparison with microservices promise (<500ms) highlights the problem
- Timer data proves the problem isn't perception - it's real 7+ seconds

### Phase 2: Microservices Architecture

**Event-Driven Architecture:**
- RabbitMQ enables true async processing with topic exchange
- Events decouple services (OrderCreated → PaymentProcessed)
- Durable queues ensure reliability (messages survive restarts)
- Routing keys enable flexible message routing patterns
- Background workers process events without blocking HTTP requests

**Database-per-Service Pattern:**
- Each service owns its data (Order DB, Payment DB, Product DB, etc.)
- No shared database = no cross-service locking
- Services can choose different database technologies
- Data isolation enables independent scaling
- Trade-off: Distributed transactions become harder (need Saga pattern)

**API Gateway Benefits:**
- Single entry point simplifies client integration
- Can handle cross-cutting concerns (auth, rate limiting, logging)
- Routes requests to appropriate microservices
- Can aggregate responses from multiple services
- Shields internal service structure from clients

**Performance Gains from Async Processing:**
- Monolith: 7,600ms (user waits for everything)
- Microservices: 13ms initial response (583x faster!)
- Payment and email happen in background
- User gets immediate feedback, not stuck waiting
- Better UX even though total processing time is similar

**Clean Architecture Benefits:**
- **Testability**: Can mock infrastructure, test business logic in isolation
- **Maintainability**: Changes isolated to specific layers
- **Flexibility**: Easy to swap databases or frameworks
- **Clarity**: Obvious where code belongs (API vs Core vs Domain vs Infrastructure)
- **Repository Pattern**: Abstracts data access, easy to mock for testing
- **Service Layer**: Business logic reusable across different APIs/interfaces

**Service-to-Service Communication:**
- Cart Service calls Product Service to get product details
- HTTP-based synchronous communication for queries
- Event-based asynchronous communication for commands
- Each pattern has appropriate use cases
- Need proper error handling and retry logic

**Redux Toolkit State Management:**
- Significantly reduces boilerplate vs raw Redux
- createSlice combines actions, reducers, selectors
- createAsyncThunk handles async API calls cleanly
- Easier to reason about state changes
- Better developer experience with built-in DevTools

**Production Best Practices:**
- Proper folder structure improves navigation and onboarding
- Shared utilities (events, logging) ensure consistency
- Environment configuration templates (.env.example)
- Service-specific documentation (README per service)
- Test structure (unit, integration, fixtures)
- Infrastructure as Code folders (docker, k8s, terraform)

---

## Resources Used
- System Design Learning Curriculum (claude.md)

---

## Questions & Parking Lot
(Topics to revisit or questions that came up)

---

## Action Items for Next Session
1. **Apply Clean Architecture to Remaining Services**
   - Refactor User, Cart, Order, Payment, Email services with layered architecture
   - Implement repository pattern across all services
   - Add service layer separation

2. **Begin Phase 3: Scalability & Performance**
   - Implement caching layer (Redis) for product catalog
   - Add load balancer with multiple service instances
   - Set up connection pooling for databases
   - Implement rate limiting in API Gateway

3. **Add Comprehensive Testing**
   - Unit tests for business logic (service layer)
   - Integration tests for API endpoints
   - E2E tests for user flows
   - Load testing (simulate Black Friday scenario)

4. **Observability & Monitoring (Phase 6 Early Start)**
   - Add distributed tracing (Jaeger or Zipkin)
   - Implement structured logging across all services
   - Set up metrics collection (Prometheus)
   - Create Grafana dashboards

---

## Notes for Future Sessions

### How to Resume
1. Read this PROGRESS.md file first
2. Check "Current Phase" and "Last Updated" at the top
3. Review "Next Steps" from the last session
4. Check the relevant phase in claude.md for context

### Updating This File
- Update after each significant milestone
- Add session notes when making important decisions
- Track "Next Steps" for easy resumption
- Move completed items from "In Progress" to "Completed"
