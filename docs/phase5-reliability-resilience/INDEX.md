# Phase 5: Reliability & Resilience - Index

## Overview

**Total Content:** ~50 KB
**Estimated Reading Time:** 90-120 minutes
**Difficulty:** Intermediate to Advanced

This phase covers building distributed systems that gracefully handle failures through fault tolerance patterns, high availability strategies, and chaos engineering.

---

## 📚 Documents

### [reliability-resilience.md](./reliability-resilience.md) (~50 KB)

**Complete guide to building reliable distributed systems**

---

## 🎯 Quick Reference

### Fault Tolerance Patterns

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| **Circuit Breaker** | Stop calling failing services | External APIs, microservices |
| **Bulkhead** | Isolate resources | Prevent resource exhaustion |
| **Retry with Backoff** | Handle transient failures | Network requests, DB queries |
| **Timeout** | Prevent indefinite blocking | All I/O operations |
| **Fallback** | Provide alternative response | Non-critical features |

### Availability Targets

| Availability | Downtime/Year | Downtime/Month | Use Case |
|--------------|---------------|----------------|----------|
| 99% (Two nines) | 3.65 days | 7.2 hours | Internal tools |
| 99.9% (Three nines) | 8.76 hours | 43.8 minutes | Standard SaaS |
| 99.95% | 4.38 hours | 21.9 minutes | Business-critical |
| 99.99% (Four nines) | 52.56 minutes | 4.38 minutes | Financial systems |
| 99.999% (Five nines) | 5.26 minutes | 26 seconds | Mission-critical |

### Health Check Types

| Type | Purpose | Kubernetes Usage | Failure Action |
|------|---------|------------------|----------------|
| **Liveness** | Is app running? | Restart if fails | Restart pod |
| **Readiness** | Can serve traffic? | Route traffic | Remove from LB |
| **Startup** | Finished starting? | Wait before checking liveness | Wait |

---

## 🗺️ Content Map

### Section 1: Fault Tolerance Patterns (~25 KB, 45 min)
- **1.1 Circuit Breaker** - Prevent cascading failures
  - Three states: CLOSED, OPEN, HALF_OPEN
  - Implementation with Python
  - Netflix Hystrix example

- **1.2 Bulkhead Pattern** - Resource isolation
  - Thread pool isolation
  - Connection pool separation
  - Multi-tenant isolation

- **1.3 Retry with Exponential Backoff** - Handle transient failures
  - Backoff formula and jitter
  - Decorator pattern implementation
  - Retryable vs non-retryable errors

- **1.4 Timeout Management** - Prevent blocking
  - Timeout hierarchy (connection, read, operation)
  - Async timeout patterns
  - Best practices

- **1.5 Fallback Strategies** - Alternative responses
  - Fallback hierarchy
  - Stale data fallback
  - Graceful degradation

### Section 2: High Availability (~15 KB, 30 min)
- **2.1 Redundancy and Failover**
  - Active-passive (cold standby)
  - Active-active (hot standby)
  - Database replication with automatic failover

- **2.2 Health Checks and Monitoring**
  - Liveness, readiness, startup probes
  - Kubernetes health check configuration
  - Dependency checking

- **2.3 SLAs, SLOs, and SLIs**
  - Definitions and examples
  - Downtime calculations
  - Error budget management

### Section 3: Chaos Engineering (~10 KB, 20 min)
- **3.1 Principles** - Proactive failure testing
  - Four-step process
  - Starting small and automating

- **3.2 Common Experiments**
  - Network latency injection
  - Service unavailability
  - Resource exhaustion
  - Database connection failure

- **3.3 Chaos Tools**
  - Chaos Monkey (Netflix)
  - Gremlin (Failure as a Service)
  - Chaos Mesh (Kubernetes)

- **3.4 GameDay Exercises**
  - Planning and execution
  - Success criteria
  - Documentation and learnings

---

## ✅ Learning Checklist

### Fault Tolerance Patterns
- [ ] Understand circuit breaker states and transitions
- [ ] Implement circuit breaker in your preferred language
- [ ] Know when to use bulkhead pattern
- [ ] Calculate exponential backoff with jitter
- [ ] Distinguish retryable vs non-retryable errors
- [ ] Set appropriate timeouts for different operations
- [ ] Design fallback hierarchy for critical features

### High Availability
- [ ] Compare active-passive vs active-active architectures
- [ ] Implement proper health check endpoints
- [ ] Understand liveness vs readiness vs startup probes
- [ ] Define SLIs for your system
- [ ] Set realistic SLOs based on business needs
- [ ] Calculate downtime from availability percentage
- [ ] Manage error budget for deployment decisions

### Chaos Engineering
- [ ] Understand chaos engineering principles
- [ ] Run a chaos experiment in staging
- [ ] Inject network latency and measure impact
- [ ] Simulate service failure and verify resilience
- [ ] Use chaos engineering tools (Chaos Mesh, Gremlin)
- [ ] Plan and execute a GameDay exercise
- [ ] Document learnings and create action items

---

## 💡 Key Concepts

### Circuit Breaker States
```
CLOSED → (failures exceed threshold) → OPEN
OPEN → (timeout expires) → HALF_OPEN
HALF_OPEN → (success) → CLOSED
HALF_OPEN → (failure) → OPEN
```

### Retry Decision Tree
```
Is error transient? (5xx, timeout, network)
├─ YES → Retry with exponential backoff
└─ NO → (4xx, validation) → Don't retry, return error
```

### Error Budget Formula
```
Error Budget = 1 - SLO Target
Remaining Budget = (Allowed Errors - Actual Errors) / Allowed Errors

Example (99.9% SLO):
- Error Budget = 0.1% (0.001)
- With 100k requests, allowed errors = 100
- If 50 errors occurred, remaining = 50%
```

### Availability Calculation
```
Availability = (Total Time - Downtime) / Total Time

Example:
- 30 days = 43,200 minutes
- 99.9% SLO allows 43.2 minutes downtime
- If 20 minutes downtime → 99.95% actual
```

---

## 🛠️ Hands-On Exercises

### Exercise 1: Circuit Breaker Implementation
**Time:** 30 minutes
**Difficulty:** Medium

Implement a circuit breaker for an unreliable API:
- Track failure count
- Transition between states
- Provide fallback response when open
- Test with simulated failures

### Exercise 2: Health Check Endpoints
**Time:** 20 minutes
**Difficulty:** Easy

Create health check endpoints for a web service:
- `/health/live` - Basic liveness check
- `/health/ready` - Database and cache connectivity
- `/health/startup` - Migrations and warmup status
- Deploy to Kubernetes with proper probe configuration

### Exercise 3: Error Budget Analysis
**Time:** 15 minutes
**Difficulty:** Easy

Given:
- SLO: 99.9% availability over 30 days
- Current: 99.85% availability

Calculate:
- How much error budget remains?
- Can we proceed with risky deployment?
- How many more errors can occur before SLO breach?

### Exercise 4: Chaos Experiment
**Time:** 45 minutes
**Difficulty:** Hard

Run a chaos experiment:
1. Deploy application to Kubernetes
2. Use Chaos Mesh to inject 100ms network latency
3. Measure impact on response times
4. Inject pod failures and verify auto-recovery
5. Document findings and improvements

---

## 📊 Pattern Decision Guide

### When to Use Each Pattern

**Circuit Breaker:**
- ✅ Calling external APIs
- ✅ Microservice communication
- ✅ Database queries that may timeout
- ❌ Internal function calls

**Bulkhead:**
- ✅ Multi-tenant systems
- ✅ Mixing critical and non-critical services
- ✅ Preventing resource exhaustion
- ❌ Single-tenant, single-service apps

**Retry with Backoff:**
- ✅ Transient network failures
- ✅ Database deadlocks
- ✅ Rate-limited APIs
- ❌ Validation errors (4xx)
- ❌ Authorization failures

**Timeout:**
- ✅ ALL network I/O operations
- ✅ Database queries
- ✅ External API calls
- ✅ File operations
- ❌ CPU-bound calculations

**Fallback:**
- ✅ Non-critical features (recommendations, reviews)
- ✅ When cached data is acceptable
- ✅ When degraded experience is better than no experience
- ❌ Critical operations (payments, auth)

---

## 🎓 Prerequisites

**Before starting this phase, you should understand:**
- Basic networking concepts (TCP, HTTP)
- Error handling in your programming language
- Asynchronous programming
- HTTP status codes
- Database connection pools

**From previous phases:**
- Phase 1: Distributed systems fundamentals
- Phase 2: Microservices architecture
- Phase 3: Load balancing and caching

---

## 📈 Progress Tracking

### Estimated Timeline
- **Reading:** 90-120 minutes
- **Hands-on exercises:** 2-3 hours
- **Total:** 3.5-5 hours

### Completion Criteria
- [ ] Read all sections of reliability-resilience.md
- [ ] Complete all learning checklist items
- [ ] Implement at least 2 fault tolerance patterns
- [ ] Run at least 1 chaos experiment
- [ ] Set up health checks for a real application
- [ ] Define SLOs for a system you're building

---

## 🔗 Related Topics

**From Other Phases:**
- Phase 1: Design for Failure principle
- Phase 2: Microservices resilience patterns
- Phase 3: Load balancing health checks
- Phase 6: Observability for detecting failures
- Phase 8: Kubernetes reliability features

**Next Steps:**
- Study Phase 6 to learn how to observe these patterns in action
- Implement monitoring and alerting for circuit breaker states
- Set up distributed tracing to understand failure propagation

---

## 📝 Notes

This documentation is part of a comprehensive system design learning journey. All examples are production-ready patterns used by companies like Netflix, Google, Amazon, and other major tech companies.

**Token Conservation:**
Do not read this file unless the user explicitly asks about reliability, resilience, fault tolerance, chaos engineering, high availability, circuit breakers, or related topics.
