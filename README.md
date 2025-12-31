# System Design Lab

[![WIP](https://img.shields.io/badge/Status-Work%20In%20Progress-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Microservices](https://img.shields.io/badge/Architecture-Microservices-green.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

> 🚧 **Work In Progress** - A developer's hands-on learning journey from monolithic applications to distributed microservices architecture

## 🎯 Overview

**This is a work-in-progress learning repository** documenting my personal journey from building monolithic applications to mastering distributed system design patterns. It features two complete implementations of an e-commerce platform that I'm actively developing and improving:

- **Monolithic Architecture** - Traditional single-application approach
- **Microservices Architecture** - Modern distributed system with event-driven communication

**Note:** This project is continuously evolving as I learn new patterns and concepts. Check the [Learning Path](#-learning-path) section to see what's implemented and what's coming next. This is also a journey to discover the deep capabilities of **Claude Code** as a development partner in building complex distributed systems.

**Perfect for:** Software engineers, system architects, and students who want to follow along with a real-world learning journey into scalable system design, microservices patterns, and distributed architectures.

## ✨ Key Features

- 🏗️ **Two Complete Architectures** - Side-by-side comparison of monolith vs microservices
- 🐳 **Fully Dockerized** - One-command setup for both environments
- 📨 **Event-Driven Communication** - RabbitMQ message broker for async operations
- 📚 **Comprehensive Documentation** - Detailed guides on distributed systems concepts
- 🔧 **Production-Ready Patterns** - Circuit breakers, health checks, proper error handling
- 🎯 **Real-World Use Case** - E-commerce platform with orders, payments, cart, and products
- ⚡ **Modern Stack** - FastAPI, React with Redux, PostgreSQL, TypeScript
- 🤖 **AI-Assisted Development** - Built with Claude Code to explore AI capabilities in complex system design

## 📖 What You'll Learn

### Architecture Patterns
- Monolithic vs Microservices trade-offs
- Service decomposition strategies
- API Gateway pattern
- Database per service pattern
- Event-driven architecture

### Distributed Systems Concepts
- Asynchronous messaging with RabbitMQ
- Service-to-service communication
- Data consistency in distributed systems
- Resilience patterns (circuit breakers, retries)
- Observability and monitoring

### Implementation Details
- Docker and Docker Compose orchestration
- RESTful API design
- JWT authentication
- Database design and migrations
- Frontend state management with Redux

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 8GB+ RAM recommended

### Run the Monolith

```bash
cd ecommerce-monolith
cp backend/.env.example backend/.env
docker-compose up -d
```

Access:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Run the Microservices

```bash
cd ecommerce-microservices
cp .env.example .env
docker-compose up -d
```

Access:
- Frontend: http://localhost:3000
- API Gateway: http://localhost:9000
- RabbitMQ Management: http://localhost:15672 (user: `ecommerce`, pass: `ecommerce123`)
- MailHog UI: http://localhost:8026

## 📁 Repository Structure

```
system-design-lab/
├── ecommerce-monolith/          # Monolithic implementation
│   ├── backend/                 # FastAPI application
│   ├── frontend/                # React application
│   └── docker-compose.yml       # Single-stack deployment
│
├── ecommerce-microservices/     # Microservices implementation
│   ├── api-gateway/             # Entry point for all requests
│   ├── services/
│   │   ├── user-service/        # Authentication & user management
│   │   ├── product-service/     # Product catalog (hexagonal architecture)
│   │   ├── cart-service/        # Shopping cart
│   │   ├── order-service/       # Order creation & management
│   │   ├── payment-service/     # Async payment processing
│   │   └── email-service/       # Email notifications
│   ├── frontend/                # React with Redux
│   ├── docs/                    # Learning materials & guides
│   └── docker-compose.yml       # Multi-service orchestration
│
└── docs/                        # Additional documentation
```

## 🎓 Learning Path

This repository follows a structured learning curriculum:

### Phase 1: Foundation (You are here)
- [x] Monolith implementation
- [x] Microservices implementation
- [x] Docker containerization
- [x] Event-driven communication

### Phase 2: Advanced Patterns (Next steps)
- [ ] Add caching layer (Redis)
- [ ] Implement circuit breakers
- [ ] Add distributed tracing
- [ ] Service mesh exploration

### Phase 3: Scalability
- [ ] Load balancing
- [ ] Database replication
- [ ] Horizontal scaling
- [ ] Performance optimization

### Phase 4: Production Readiness
- [ ] CI/CD pipeline
- [ ] Kubernetes deployment
- [ ] Monitoring & observability
- [ ] Security hardening

See [CLAUDE.md](CLAUDE.md) for the complete learning roadmap.

## 🔍 Key Implementations

### Monolith Architecture
- Single FastAPI application
- Shared database
- Synchronous operations
- Simple deployment model

**When to use:** Small teams, simple domains, rapid prototyping, limited scale requirements

### Microservices Architecture
- 6 independent services
- Database per service
- Asynchronous messaging with RabbitMQ
- API Gateway pattern
- Event-driven communication

**When to use:** Large teams, complex domains, independent scaling needs, polyglot persistence

## 📚 Documentation

### Getting Started
- [Monolith Guide](ecommerce-monolith/README.md) - Setup and architecture
- [Microservices Guide](ecommerce-microservices/README.md) - Setup and architecture
- [Environment Setup](ecommerce-microservices/ENV_SETUP.md) - Configuration guide

### 📖 Comprehensive Learning Path

#### Phase 1: Fundamentals (~4 hours, 119 KB)
**Location:** `/docs/fundamentals/`

A complete foundation in distributed systems concepts:
- **[Monolith Limitations](docs/fundamentals/monolith-limitations.md)** (~26 KB, 45-60 min)
  - Scalability bottlenecks and cost implications
  - Deployment risks with real incident case studies
  - Technology lock-in and migration challenges
  - Team coordination at scale (Brooks's Law)

- **[Distributed Systems Fundamentals](docs/fundamentals/distributed-systems-fundamentals.md)** (~50 KB, 90-120 min)
  - CAP Theorem: CP vs AP trade-offs with real examples
  - ACID vs BASE: Different consistency philosophies
  - Network Fallacies: 8 false assumptions about networks
  - Consistency Models: From linearizable to eventual

- **[System Design Principles](docs/fundamentals/system-design-principles.md)** (~43 KB, 75-90 min)
  - Separation of Concerns: Horizontal, vertical, aspect
  - Single Responsibility Principle at system level
  - Loose Coupling, High Cohesion: Patterns and metrics
  - Design for Failure: Circuit breakers, timeouts, bulkheads

- **[Phase 1 Index](docs/fundamentals/INDEX.md)** - Navigation, progress tracking, and learning guide

**Features:** 50+ real-world examples, 60+ diagrams, complete code samples, progress checklists

#### Phase 2: Architecture Patterns (~4.5 hours, 121 KB)
**Location:** `/docs/phase2-architecture-patterns/`

Deep dive into specific architectural patterns for distributed systems:

- **[Microservices Architecture](docs/phase2-architecture-patterns/microservices-architecture.md)** (~40 KB, 75-90 min)
  - Service boundaries using Domain-Driven Design
  - Communication patterns: Synchronous (REST/gRPC) vs Asynchronous (Queues/Streaming)
  - Service Mesh concepts (Istio, Linkerd)
  - API Gateway pattern and Backend for Frontend (BFF)

- **[Event-Driven Architecture](docs/phase2-architecture-patterns/event-driven-architecture.md)** (~43 KB, 80-100 min)
  - Event Sourcing: Complete implementation examples
  - CQRS: Separate read and write models
  - Event Streaming (Kafka) vs Messaging (RabbitMQ)
  - Saga Pattern: Distributed transactions (Choreography vs Orchestration)

- **[Architectural Patterns](docs/phase2-architecture-patterns/architectural-patterns.md)** (~38 KB, 70-85 min)
  - Layered Architecture: Traditional 3-tier
  - Hexagonal Architecture: Ports & Adapters
  - Clean Architecture: Dependency rule and concentric circles
  - Strangler Fig Pattern: Incremental legacy migration

- **[Phase 2 Index](docs/phase2-architecture-patterns/INDEX.md)** - Pattern decision matrices, exercises, integration guide

**Features:** 75+ code samples, pattern comparison tables, hands-on exercises, real-world case studies

#### Phase 3: Scalability & Performance (~2 hours, 50 KB)
**Location:** `/docs/phase3-scalability-performance/`

Techniques for building systems that scale and perform:

- **[Scalability & Performance](docs/phase3-scalability-performance/scalability-performance.md)** (~50 KB, 90-120 min)
  - **Caching Strategies:** Cache-aside, write-through, write-behind, CDN, Redis patterns
  - **Load Balancing:** L4 vs L7, algorithms (round robin, least connections), health checks
  - **Database Scaling:** Read replicas, sharding strategies, connection pooling
  - **Performance Optimization:** Query optimization, denormalization, async processing

- **[Phase 3 Index](docs/phase3-scalability-performance/INDEX.md)** - Quick reference, decision criteria, checklists

**Features:** Complete code examples, real-world patterns, trade-off analysis, hands-on exercises

#### Phase 4: Data Management (~2 hours, 40 KB)
**Location:** `/docs/phase4-data-management/`

Master data storage and consistency in distributed systems:

- **[Data Management](docs/phase4-data-management/data-management.md)** (~40 KB, 75-90 min)
  - **Database Types & Use Cases:** Polyglot persistence strategy
    - Relational (PostgreSQL, MySQL): ACID, transactions, referential integrity
    - Document (MongoDB): Flexible schema, nested data
    - Key-Value (Redis): Extreme speed, caching, sessions
    - Column-Family (Cassandra): Massive scale, time-series
    - Graph (Neo4j): Relationships, traversals
    - Time-Series (InfluxDB, Prometheus): Metrics, monitoring
  - **Data Consistency Patterns:** Two-Phase Commit (2PC), Saga pattern, Idempotency
  - **Data Replication:** Master-slave, multi-master, quorum-based replication

- **[Phase 4 Index](docs/phase4-data-management/INDEX.md)** - Database selection criteria, consistency patterns, replication guide

**Features:** Database comparison matrices, complete implementation examples, conflict resolution strategies, hands-on exercises

#### Phase 5: Reliability & Resilience (~2 hours, 50 KB)
**Location:** `/docs/phase5-reliability-resilience/`

Build systems that gracefully handle failures:

- **[Reliability & Resilience](docs/phase5-reliability-resilience/reliability-resilience.md)** (~50 KB, 90-120 min)
  - **Fault Tolerance Patterns:** Circuit breaker, Bulkhead, Retry with backoff, Timeout, Fallback
  - **High Availability:** Redundancy, health checks, SLAs/SLOs/SLIs, error budgets
  - **Chaos Engineering:** Principles, experiments, tools (Chaos Monkey, Gremlin, Chaos Mesh)

- **[Phase 5 Index](docs/phase5-reliability-resilience/INDEX.md)** - Pattern decision guide, availability calculations, GameDay exercises

**Features:** Production-ready patterns, complete implementations, chaos engineering examples, hands-on exercises

#### Phase 6: Observability & Monitoring (~2 hours, 50 KB)
**Location:** `/docs/phase6-observability-monitoring/`

Understand and debug distributed systems:

- **[Observability & Monitoring](docs/phase6-observability-monitoring/observability-monitoring.md)** (~50 KB, 90-120 min)
  - **Three Pillars:** Metrics (Prometheus), Logs (ELK), Traces (OpenTelemetry)
  - **Monitoring Methods:** RED (services), USE (resources), Golden Signals
  - **Distributed Tracing:** OpenTelemetry, Jaeger, context propagation
  - **Alerting:** Design principles, alert fatigue prevention, on-call practices

- **[Phase 6 Index](docs/phase6-observability-monitoring/INDEX.md)** - Quick reference, tool comparisons, alerting best practices

**Features:** Complete observability stack, PromQL queries, Grafana dashboards, incident response runbooks

#### Phase 7: Security & Identity (~2 hours, 45 KB)
**Location:** `/docs/phase7-security-identity/`

Secure distributed systems through authentication and authorization:

- **[Security & Identity](docs/phase7-security-identity/security-identity.md)** (~45 KB, 80-100 min)
  - **Authentication:** JWT, sessions, OAuth 2.0, mTLS
  - **Authorization:** RBAC (Role-Based Access Control)
  - **Secrets Management:** HashiCorp Vault, environment variables, key rotation
  - **API Security:** Rate limiting, input validation, CORS, SQL injection prevention
  - **Zero Trust Architecture:** Principles and implementation

- **[Phase 7 Index](docs/phase7-security-identity/INDEX.md)** - Security checklist, OWASP Top 10, auth method comparison

**Features:** Production security patterns, JWT/OAuth implementations, secrets management, security audit checklist

#### Phase 8: Deployment & DevOps (~1.5 hours, 40 KB)
**Location:** `/docs/phase8-deployment-devops/`

Modern deployment practices and automation:

- **[Deployment & DevOps](docs/phase8-deployment-devops/deployment-devops.md)** (~40 KB, 75-90 min)
  - **Containerization:** Docker best practices, multi-stage builds, Docker Compose
  - **Kubernetes:** Deployments, Services, Ingress, HPA, ConfigMaps, Secrets
  - **CI/CD:** GitHub Actions, GitLab CI, automated testing and deployment
  - **Deployment Strategies:** Rolling update, blue-green, canary
  - **Infrastructure as Code:** Terraform, Helm charts

- **[Phase 8 Index](docs/phase8-deployment-devops/INDEX.md)** - Deployment strategy comparison, tool selection guide

**Features:** Production Dockerfiles, K8s manifests, complete CI/CD pipelines, IaC templates

#### Phase 9: Real-World System Design (~2 hours, 50 KB)
**Location:** `/docs/phase9-real-world-systems/`

Case studies of large-scale distributed systems:

- **[Real-World Systems](docs/phase9-real-world-systems/real-world-systems.md)** (~50 KB, 90-120 min)
  - **URL Shortener (bit.ly):** Base62 encoding, caching, analytics
  - **Social Media Feed (Twitter):** Hybrid fan-out strategy
  - **Video Streaming (YouTube):** Adaptive bitrate (HLS), multi-tier CDN
  - **E-commerce (Amazon):** Inventory management, Saga pattern, Elasticsearch
  - **Ride-Sharing (Uber):** Geospatial indexing, driver-rider matching
  - **Messaging (WhatsApp):** Delivery guarantees, Cassandra, presence system

- **[Phase 9 Index](docs/phase9-real-world-systems/INDEX.md)** - System summaries, design exercises, interview preparation

**Features:** 6 complete case studies, capacity estimations, trade-off analysis, interview-ready designs

#### Phase 10: Advanced Topics (~1.5 hours, 40 KB)
**Location:** `/docs/phase10-advanced-topics/`

Cutting-edge technologies and optimization:

- **[Advanced Topics](docs/phase10-advanced-topics/advanced-topics.md)** (~40 KB, 75-90 min)
  - **Serverless:** AWS Lambda, cold start mitigation, Serverless Framework
  - **Edge Computing:** Cloudflare Workers, Lambda@Edge
  - **Modern APIs:** GraphQL (DataLoader, N+1), gRPC (Protocol Buffers, streaming)
  - **Service Mesh:** Istio (traffic management, mTLS, observability)
  - **Performance:** Query optimization, connection pooling, multi-level caching
  - **Emerging:** WebAssembly, CRDTs, Event Sourcing

- **[Phase 10 Index](docs/phase10-advanced-topics/INDEX.md)** - Technology decision matrix, performance comparisons

**Features:** Serverless examples, GraphQL/gRPC implementations, service mesh setup, optimization techniques

### Architecture Deep Dives
- [Microservices Architecture](ecommerce-microservices/ARCHITECTURE.md) - Design decisions
- [Service Communication](ecommerce-microservices/docs/SERVICE_COMMUNICATION.md) - Sync vs async
- [Message Broker Fundamentals](ecommerce-microservices/docs/MESSAGE_BROKER_FUNDAMENTALS.md) - RabbitMQ patterns

### Practical Guides
- [Complete Documentation Index](ecommerce-microservices/docs/INDEX.md)
- [Docker & Data Persistence](ecommerce-microservices/docs/DATA_PERSISTENCE_DEMO.md)
- [Queue Systems Comparison](ecommerce-microservices/docs/QUEUE_SYSTEMS_COMPARISON.md)
- [Payment Gateway Patterns](ecommerce-microservices/docs/PAYMENT_GATEWAY_REAL_WORLD.md)

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15
- **Message Broker:** RabbitMQ
- **Authentication:** JWT
- **Email Testing:** MailHog

### Frontend
- **Framework:** React 18 with TypeScript
- **State Management:** Redux Toolkit
- **Build Tool:** Vite
- **Styling:** CSS Modules

### DevOps
- **Containerization:** Docker
- **Orchestration:** Docker Compose
- **Environment Management:** dotenv

## 🧪 Testing

Each implementation includes:
- Unit tests for business logic
- Integration tests for API endpoints
- Docker health checks

```bash
# Run tests in monolith
cd ecommerce-monolith/backend
pytest

# Run tests in microservices
cd ecommerce-microservices/services/product-service
pytest
```

## 📈 Roadmap

- [x] Basic monolith implementation
- [x] Basic microservices implementation
- [x] Event-driven architecture with RabbitMQ
- [x] Comprehensive documentation
- [ ] Add Redis caching layer
- [ ] Implement distributed tracing (Jaeger)
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Kubernetes deployment manifests
- [ ] CI/CD with GitHub Actions
- [ ] Load testing scenarios

## 🤝 Contributing

Contributions are welcome! **This is a learning-in-progress repository**, so I especially appreciate:
- Suggestions for improvements or corrections
- Additional patterns and best practices
- Bug fixes and documentation improvements
- Your own learning experiences and insights

Since we're all learning together, don't hesitate to contribute even if you're not 100% sure - that's how we all grow!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-pattern`)
3. Commit your changes (`git commit -m 'Add circuit breaker pattern'`)
4. Push to the branch (`git push origin feature/amazing-pattern`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by real-world system design challenges
- Built as I learn - sharing my journey with the software engineering community
- Developed with **[Claude Code](https://claude.com/claude-code)** - exploring the capabilities of AI-assisted development for complex distributed systems
- Special thanks to the open-source projects that made this possible (FastAPI, React, RabbitMQ, PostgreSQL)

## 📧 Contact

Have questions or suggestions? Feel free to open an issue or reach out! I'm learning too, so let's learn together.

---

**⭐ If you find this helpful, please star the repository!**

Made with ❤️ by a developer learning system design in public
