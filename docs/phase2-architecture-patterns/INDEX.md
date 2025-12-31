# Architecture Patterns - Index

## Overview

This directory contains comprehensive educational materials for **Phase 2: Architecture Patterns** of the system design learning journey. Building on the fundamentals from Phase 1, these documents dive deep into specific architectural patterns used in modern distributed systems.

**Prerequisites:** Complete Phase 1 (Fundamentals) before starting Phase 2.

**Learning Goal:** Learn common architectural patterns and when to use them.

---

## 📚 Available Documents

### 1. Microservices Architecture
**File:** `microservices-architecture.md`
**Size:** ~40 KB
**Reading Time:** 75-90 minutes

#### What You'll Learn
The complete guide to building distributed systems with microservices:

1. **Service Boundaries and Sizing** (10 KB)
   - Domain-Driven Design approach to finding boundaries
   - Business capability mapping
   - How small is "micro"? (Nanoservices vs right-sized services)
   - Two-Pizza Team Rule
   - Indicators you got boundaries wrong
   - Real-world example: Amazon's evolution

2. **Communication Patterns** (12 KB)
   - **Synchronous:** HTTP/REST and gRPC
   - **Asynchronous:** Message queues and pub/sub
   - Latency, coupling, and reliability trade-offs
   - When to use synchronous vs asynchronous
   - Hybrid approaches (real-world examples)
   - Complete code examples for each pattern

3. **Service Mesh Concepts** (10 KB)
   - What problems service meshes solve
   - Sidecar pattern architecture
   - Data plane (Envoy proxy) vs control plane (Istio)
   - Traffic management (retries, circuit breaking, load balancing)
   - Security (automatic mTLS, authorization)
   - Observability (metrics, tracing)
   - Popular options: Istio, Linkerd, Consul Connect, AWS App Mesh
   - When to use (and when not to use) service mesh

4. **API Gateway Pattern** (8 KB)
   - Single entry point for clients
   - Request routing and aggregation
   - Backend for Frontend (BFF) pattern
   - Authentication and authorization
   - Rate limiting and caching
   - Response transformation
   - Popular solutions: Kong, AWS API Gateway, Envoy, NGINX
   - Anti-patterns to avoid

#### Key Takeaways
- Service boundaries should align with business capabilities
- Communication patterns have significant trade-offs
- Service mesh solves cross-cutting concerns at infrastructure level
- API Gateway simplifies client integration

#### Real-World Examples
- Amazon's service evolution (monolith to hundreds of services)
- Netflix service mesh usage
- E-commerce system with API Gateway
- Mobile vs Web Backend for Frontend

---

### 2. Event-Driven Architecture
**File:** `event-driven-architecture.md`
**Size:** ~43 KB
**Reading Time:** 80-100 minutes

#### What You'll Learn
Comprehensive guide to building reactive, event-driven systems:

1. **Event Sourcing** (12 KB)
   - Store events, not state
   - Complete implementation example (Order system)
   - Rebuilding state from events
   - Snapshot pattern for performance
   - Event schema evolution
   - Benefits: Audit trail, temporal queries, event replay
   - Challenges: Complexity, querying difficulty
   - When to use (finance, audit requirements) vs when not to

2. **CQRS (Command Query Responsibility Segregation)** (11 KB)
   - Separate read and write models
   - Commands (write side) vs Queries (read side)
   - Multiple read models for different query patterns
   - Complete implementation (e-commerce orders)
   - Event bus connecting write and read sides
   - Benefits: Independent scaling, optimized models
   - Eventual consistency challenges
   - CQRS without event sourcing

3. **Event Streaming vs Messaging** (10 KB)
   - **Messaging (RabbitMQ, SQS):**
     - Point-to-point and pub/sub
     - Messages deleted after consumption
     - Task queues and command processing
   - **Event Streaming (Kafka, Kinesis):**
     - Append-only log
     - Events retained for replay
     - Stream processing and analytics
   - Detailed comparison table
   - When to use each
   - Complete code examples

4. **Saga Pattern** (10 KB)
   - Distributed transactions across microservices
   - **Choreography-based:** Event-driven coordination
   - **Orchestration-based:** Central coordinator
   - Compensating transactions for rollback
   - Idempotency handling
   - Timeout strategies
   - Real implementation examples
   - Saga vs traditional ACID transactions

#### Key Takeaways
- Event sourcing provides complete audit trail but adds complexity
- CQRS optimizes reads and writes independently
- Choose messaging for tasks, streaming for event history
- Sagas enable distributed transactions without 2PC

#### Real-World Examples
- Banking with event sourcing
- E-commerce with CQRS (order list vs analytics)
- Kafka vs RabbitMQ use cases
- Order processing saga (choreography vs orchestration)

---

### 3. Architectural Patterns
**File:** `architectural-patterns.md`
**Size:** ~38 KB
**Reading Time:** 70-85 minutes

#### What You'll Learn
Four fundamental patterns for organizing systems and code:

1. **Layered Architecture** (10 KB)
   - Traditional 3-tier: Presentation, Business Logic, Data Access
   - Layer responsibilities and boundaries
   - Complete implementation example
   - Benefits: Clear separation, easy to understand
   - Drawbacks: Database coupling, horizontal slicing
   - Variants: Relaxed layered, N-tier
   - When to use traditional layered architecture

2. **Hexagonal Architecture (Ports & Adapters)** (10 KB)
   - Business logic at center, isolated from external concerns
   - Ports: Interfaces defining what app needs
   - Adapters: Implementations of ports
   - Inbound adapters: REST, GraphQL, CLI
   - Outbound adapters: Database, external APIs
   - Complete hexagonal example (order system)
   - Benefits: Technology independence, highly testable
   - When to use vs when not needed

3. **Clean Architecture** (10 KB)
   - Concentric circles with dependency rule
   - **Entities:** Enterprise business rules (innermost)
   - **Use Cases:** Application business rules
   - **Interface Adapters:** Controllers, gateways, presenters
   - **Frameworks & Drivers:** External tools (outermost)
   - The dependency rule: Dependencies point inward
   - Dependency inversion for crossing boundaries
   - Complete clean architecture example
   - Benefits: Independent of frameworks, UI, database
   - Clean vs Hexagonal comparison

4. **Strangler Fig Pattern** (8 KB)
   - Incrementally migrate legacy systems
   - Avoid "big bang" rewrites
   - Step 1: Create facade/proxy
   - Step 2: Migrate incrementally (dual writes, dual reads, cutover)
   - Step 3: Anti-corruption layer
   - Feature flags and gradual rollout
   - Real-world example: Shopify's migration
   - Best practices and rollback strategies

#### Key Takeaways
- Layered: Simple, good for traditional apps
- Hexagonal: Technology-independent, great for complex domains
- Clean: Most comprehensive, dependency rule
- Strangler Fig: Safe legacy migration strategy

#### Real-World Examples
- E-commerce with layered architecture
- Order processing with hexagonal (swap Postgres for MongoDB)
- Enterprise app with clean architecture
- Shopify's strangler fig migration (PHP monolith to services)

---

## 🎯 Learning Objectives

After completing Phase 2, you should be able to:

1. **Design** microservice boundaries using Domain-Driven Design
2. **Choose** appropriate communication patterns (sync vs async)
3. **Explain** when service mesh adds value
4. **Implement** API Gateway patterns (routing, aggregation, BFF)
5. **Apply** event sourcing and CQRS to appropriate use cases
6. **Decide** between messaging and event streaming
7. **Design** distributed transactions using Saga pattern
8. **Organize** code using layered, hexagonal, or clean architecture
9. **Migrate** legacy systems using Strangler Fig pattern
10. **Evaluate** trade-offs between different architectural approaches

---

## 📖 How to Use These Documents

### Recommended Learning Path

```
Phase 1: Fundamentals (completed) ✓
    ↓
Phase 2: Start here ↓

Week 3:
├── Day 1-2: Microservices Architecture
│   ├── Service boundaries
│   └── Communication patterns
├── Day 3-4: Microservices Architecture
│   ├── Service mesh
│   └── API Gateway
└── Day 5: Practice
    └── Design a microservices system

Week 4:
├── Day 1-2: Event-Driven Architecture
│   ├── Event sourcing
│   └── CQRS
├── Day 3-4: Event-Driven Architecture
│   ├── Streaming vs messaging
│   └── Saga pattern
└── Day 5: Architectural Patterns
    ├── Layered, hexagonal, clean
    └── Strangler fig

End of Week 4:
└── Practical exercise: Implement event-driven system
```

### Study Method

**For Deep Learning:**
1. Read one section at a time (don't rush)
2. Run the code examples (type them out, don't copy-paste)
3. Modify examples to test understanding
4. Sketch architectures on paper/whiteboard
5. Relate to systems you've worked with

**For Reference:**
- Use INDEX to quickly find topics
- Code examples can be used as templates
- Comparison tables for decision-making

### Hands-On Exercises

**After Microservices Architecture:**
```
Exercise 1: Design Microservices
├── Take a monolithic system you know
├── Identify bounded contexts
├── Draw service boundaries
├── Design communication patterns
└── Document why you made each choice

Exercise 2: Build Simple Microservices
├── Create 2-3 services (User, Order, Product)
├── Implement synchronous (REST) communication
├── Add asynchronous (RabbitMQ or Kafka) communication
├── Add API Gateway
└── Deploy and test
```

**After Event-Driven Architecture:**
```
Exercise 3: Event Sourcing
├── Build order service with event sourcing
├── Store events (OrderCreated, OrderShipped, etc.)
├── Rebuild order state from events
├── Implement snapshot pattern
└── Query historical state

Exercise 4: Saga Pattern
├── Implement distributed transaction (order → payment → inventory)
├── Try choreography-based saga
├── Try orchestration-based saga
├── Implement compensating transactions
└── Test failure scenarios
```

**After Architectural Patterns:**
```
Exercise 5: Refactor to Hexagonal
├── Take existing code
├── Identify business logic
├── Extract to core (domain)
├── Define ports (interfaces)
├── Implement adapters
└── Test business logic without database

Exercise 6: Strangler Fig
├── Take small legacy app
├── Add proxy in front
├── Extract one feature as new service
├── Route some traffic to new service
└── Gradually increase traffic percentage
```

---

## 🔗 Related Materials

### Prerequisites (Phase 1)
**Must complete before Phase 2:**
- `/docs/fundamentals/monolith-limitations.md` - Why distributed systems?
- `/docs/fundamentals/distributed-systems-fundamentals.md` - CAP, ACID vs BASE
- `/docs/fundamentals/system-design-principles.md` - SRP, loose coupling, design for failure

### Practical Projects
**Apply Phase 2 concepts:**
- `/ecommerce-microservices/` - Hands-on microservices project
- `/ecommerce-microservices/docs/` - Additional technical deep-dives
  - Service communication patterns
  - Message broker fundamentals
  - Queue systems comparison

### Next Steps (Phase 3)
**After completing Phase 2:**
- Phase 3: Scalability & Performance
  - Caching strategies
  - Load balancing
  - Database scaling
  - Asynchronous processing

---

## 💡 Pattern Decision Matrix

Use this matrix to choose the right pattern:

### Microservices vs Monolith

| Factor | Monolith | Microservices |
|--------|----------|---------------|
| Team size | < 10 | 10+ |
| System complexity | Low-Medium | High |
| Scaling needs | Uniform | Service-specific |
| Deployment frequency | Weekly/Monthly | Multiple times/day |
| Technology diversity | Not needed | Beneficial |
| Operational maturity | Low | High |

### Communication Patterns

| Need | Synchronous (REST/gRPC) | Asynchronous (Queue/Stream) |
|------|-------------------------|------------------------------|
| Immediate response | ✓ | ✗ |
| Strong consistency | ✓ | ✗ |
| Loose coupling | ✗ | ✓ |
| High throughput | ✗ | ✓ |
| Event replay | ✗ | ✓ (streaming only) |
| Simple debugging | ✓ | ✗ |

### Event Patterns

| Feature | Event Sourcing | CQRS | Saga |
|---------|----------------|------|------|
| Audit trail | ✓✓✓ | ✓ | ✓ |
| Multiple read models | ✓✓ | ✓✓✓ | ✗ |
| Distributed transactions | ✗ | ✗ | ✓✓✓ |
| Complexity | High | Medium | Medium-High |
| Storage growth | High | Medium | Low |

### Architectural Patterns

| Pattern | Complexity | Testability | Flexibility | Learning Curve |
|---------|------------|-------------|-------------|----------------|
| Layered | Low | Medium | Low | Low |
| Hexagonal | Medium | High | High | Medium |
| Clean | High | Very High | Very High | High |

---

## 📊 Document Statistics

| Document | Size | Reading Time | Sections | Examples | Code Samples |
|----------|------|--------------|----------|----------|--------------|
| Microservices | ~40 KB | 75-90 min | 4 | 15+ | 25+ |
| Event-Driven | ~43 KB | 80-100 min | 4 | 18+ | 30+ |
| Architectural Patterns | ~38 KB | 70-85 min | 4 | 12+ | 20+ |
| **Total** | **~121 KB** | **~4.5 hours** | **12** | **45+** | **75+** |

---

## ✅ Progress Checklist

### Microservices Architecture
- [ ] Read: Service Boundaries and Sizing
- [ ] Read: Communication Patterns (Sync vs Async)
- [ ] Read: Service Mesh Concepts
- [ ] Read: API Gateway Pattern
- [ ] Exercise: Design microservices for a system you know
- [ ] Exercise: Build 2-3 communicating services

### Event-Driven Architecture
- [ ] Read: Event Sourcing
- [ ] Read: CQRS
- [ ] Read: Event Streaming vs Messaging
- [ ] Read: Saga Pattern
- [ ] Exercise: Implement event sourcing
- [ ] Exercise: Build saga for distributed transaction

### Architectural Patterns
- [ ] Read: Layered Architecture
- [ ] Read: Hexagonal Architecture
- [ ] Read: Clean Architecture
- [ ] Read: Strangler Fig Pattern
- [ ] Exercise: Refactor code to hexagonal
- [ ] Exercise: Plan a strangler fig migration

### Integration
- [ ] Combine patterns: Microservices + Events + Hexagonal
- [ ] Design complete e-commerce system
- [ ] Document architectural decisions
- [ ] Present design to peers

### Ready for Phase 3
- [ ] Completed all readings
- [ ] Completed exercises
- [ ] Can explain when to use each pattern
- [ ] Can critique real-world architectures

---

## 🤔 Common Questions

**Q: Should every microservice use event sourcing?**
A: No! Event sourcing adds complexity. Use only where audit trail or event replay provides value (e.g., financial transactions, order processing). Most CRUD services don't need it.

**Q: Is service mesh required for microservices?**
A: No. Service mesh helps when you have many services (10+) and need consistent observability/security. For 2-5 services, libraries or manual implementation may suffice.

**Q: CQRS without event sourcing?**
A: Yes! CQRS just separates reads from writes. You can use traditional database with materialized views or separate read replicas. Event sourcing is optional.

**Q: Saga vs 2PC (Two-Phase Commit)?**
A: Use saga in microservices (separate databases, can't use 2PC). Use 2PC only within single database. 2PC doesn't scale well in distributed systems.

**Q: Which architecture pattern should I use?**
A: Start with layered for simple apps. Use hexagonal when you have complex business logic or multiple integration points. Use clean for long-lived, evolving systems. Don't over-engineer.

**Q: Can I mix patterns?**
A: Absolutely! Real systems combine patterns:
- Microservices (service boundaries) + Hexagonal (within each service) + Events (communication)
- Clean architecture (code organization) + CQRS (read/write separation) + Saga (workflows)

**Q: How do I migrate from monolith?**
A: Use Strangler Fig pattern. Don't attempt big bang rewrite. Extract one service at a time, starting with bounded contexts that are least coupled to the rest.

**Q: Do I need to read all of Phase 1 first?**
A: Yes! Phase 2 assumes you understand CAP theorem, consistency models, network fallacies, and system design principles. Phase 1 provides the "why," Phase 2 provides the "how."

---

## 💡 Token Conservation Notice

**IMPORTANT FOR AI ASSISTANTS:**

These files are comprehensive learning materials (121 KB total) and should **NOT be read automatically** to conserve tokens.

**Only read these files when:**
1. User explicitly asks about architectural patterns
2. User references a specific pattern by name
3. Current task directly requires understanding from these docs

**Before reading:**
1. Check this INDEX to see if the topic is covered
2. Determine which specific section is relevant
3. Read only necessary sections, not entire documents

**Example good usage:**
- User asks: "How do I design microservice boundaries?" → Read `microservices-architecture.md` section 1
- User asks: "Explain event sourcing" → Read `event-driven-architecture.md` section 1
- User asks: "What's hexagonal architecture?" → Read `architectural-patterns.md` section 2

**Example bad usage:**
- User asks: "How do I debug this error?" → Don't read architecture docs
- User asks: "What is CAP theorem?" → That's Phase 1, not Phase 2

---

## 🔄 How Patterns Relate

Understanding how patterns work together:

```
System Level:
├── Microservices Architecture
│   ├── Defines service boundaries
│   └── Communication strategies
│
Service Level:
├── Hexagonal/Clean Architecture
│   ├── Organizes code within each service
│   └── Keeps business logic isolated
│
Communication Level:
├── Event-Driven Architecture
│   ├── How services interact
│   └── Event sourcing, CQRS, Saga
│
Migration Level:
└── Strangler Fig Pattern
    ├── How to get from monolith to microservices
    └── Incremental, safe migration

Use together for complete architecture!
```

**Example: E-commerce System**
```
Overall: Microservices Architecture
├── User Service (hexagonal architecture internally)
├── Order Service (clean architecture internally)
├── Product Service (layered architecture internally - simple CRUD)
└── Communication: Event-driven (Kafka)
    ├── Order processing: Saga pattern
    ├── Order history: Event sourcing
    └── Order queries: CQRS

Migration: Strangler Fig (from legacy PHP monolith)
```

---

## 📝 Practical Application Roadmap

**Week 3-4: Hands-on Project**
```
Project: Build E-commerce System

Day 1-2: Design
├── Identify bounded contexts
├── Define service boundaries
├── Choose communication patterns
└── Document decisions

Day 3-5: User & Product Services
├── Build two microservices
├── Implement hexagonal architecture
├── REST APIs for synchronous communication
└── Kafka for events

Day 6-8: Order Service with Events
├── Implement event sourcing (order events)
├── Add CQRS (order list vs analytics)
├── Build saga for order processing
└── Test compensation on failures

Day 9-10: API Gateway & Observability
├── Add API Gateway (Kong or NGINX)
├── Implement BFF for mobile
├── Add service mesh (Istio) or simple observability
└── Load test and monitor

Day 11-12: Refine & Document
├── Fix issues found in testing
├── Document architecture decisions
├── Create diagrams
└── Present to peers

Day 13-14: Explore Alternative
├── Implement one feature differently
├── Compare synchronous vs asynchronous
├── Try orchestration vs choreography saga
└── Document trade-offs
```

---

## 🚀 Ready to Start?

1. **New to architecture patterns?** Start with `microservices-architecture.md`
2. **Interested in events?** Read `event-driven-architecture.md`
3. **Need code organization?** Check `architectural-patterns.md`
4. **Migrating legacy?** Jump to Strangler Fig in `architectural-patterns.md` section 4

**Phase 2 builds on Phase 1.** If you haven't completed Phase 1 (Fundamentals), start there first!

**After Phase 2:** You'll be ready for Phase 3 (Scalability & Performance), where you'll learn caching, load balancing, database scaling, and optimization techniques.

Happy architecting! 🏗️
