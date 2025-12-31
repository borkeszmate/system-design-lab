# Learning Materials Index

This folder contains educational documents explaining key concepts related to this microservices project. These files are **reference materials** and should **NOT be read automatically** by agents unless specifically relevant to the current task.

---

## Infrastructure & Docker

### DATA_PERSISTENCE_DEMO.md
**Topic:** Docker volume lifecycle and data persistence
**Covers:** How data survives container destruction, volume types (named, bind, anonymous), backup/restore strategies
**When to read:** Questions about Docker volumes, data persistence, or database storage

### DAEMON_EXPLAINED.md
**Topic:** Difference between daemons and processes
**Covers:** Docker daemon architecture, process lifecycle, background services
**When to read:** Questions about Docker daemon, background processes, or service management

---

## Microservices Communication

### SERVICE_COMMUNICATION.md
**Topic:** How services communicate in microservices architecture
**Covers:** Synchronous HTTP (API Gateway → Order Service), Asynchronous events (RabbitMQ), complete checkout flow timeline
**When to read:** Questions about service-to-service communication, sync vs async patterns

---

## Message Brokers & Queues

### MESSAGE_BROKER_FUNDAMENTALS.md
**Topic:** Deep dive into message broker concepts
**Covers:** Producers, consumers, queues, exchanges, bindings, routing keys, ACK/NACK, topic patterns, reliability guarantees, Dead Letter Queues
**When to read:** Questions about RabbitMQ fundamentals, message broker patterns, or event-driven architecture

### QUEUE_SYSTEMS_COMPARISON.md
**Topic:** RabbitMQ vs Celery/Laravel Queues
**Covers:** Task queue alternatives, when to use each, migration paths, code comparisons, polyglot vs Python-only solutions
**When to read:** Questions about queue system alternatives, Celery, or Laravel Queue equivalents

### SOLACE_VS_RABBITMQ.md
**Topic:** Comparison of Solace PubSub+ and RabbitMQ
**Covers:** Enterprise event streaming vs microservices messaging, throughput/latency differences, IoT/manufacturing use cases, cost comparison
**When to read:** Questions about Solace, high-throughput messaging, or industrial IoT integration

---

## Payment Integration

### PAYMENT_GATEWAY_REAL_WORLD.md
**Topic:** Real-world payment gateway integration (Stripe, PayPal)
**Covers:** Direct API payments, redirect flows, webhooks, how simulation maps to real implementations
**When to read:** Questions about payment processing, 3rd party integrations, or webhook patterns

---

## Usage Instructions for Future Agents

**DO NOT read these files automatically.**

**ONLY read when:**
1. User explicitly asks about a topic covered in these docs
2. User references one of these files directly
3. The current task is directly related to the concepts explained

**To decide if relevant:**
- Check the file name and topic first
- Read the "Covers" section in this index
- Only open the full file if it directly answers the user's question

**Why?** These files are large (5-26KB each) and contain educational content that should not be loaded into context unless needed.
