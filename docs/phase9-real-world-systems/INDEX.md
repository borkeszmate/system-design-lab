# Phase 9: Real-World System Design - Index

## Overview

**Total Content:** ~50 KB
**Estimated Reading Time:** 90-120 minutes
**Difficulty:** Advanced

Case studies of large-scale distributed systems analyzing architecture, trade-offs, and engineering decisions.

---

## 📚 Documents

### [real-world-systems.md](./real-world-systems.md) (~50 KB)

**Complete case studies of 6 major system designs**

---

## 🎯 System Summaries

### 1. URL Shortener (like bit.ly)
- **Scale:** 100M URLs/month, 10B redirects/month
- **Key Challenge:** Low latency (< 10ms) redirects
- **Solution:** Aggressive caching, Base62 encoding, CDN

### 2. Social Media Feed (like Twitter)
- **Scale:** 500M users, 100M daily active
- **Key Challenge:** Timeline generation (fan-out problem)
- **Solution:** Hybrid push/pull model

### 3. Video Streaming (like YouTube)
- **Scale:** 500 hours uploaded/minute, petabyte storage
- **Key Challenge:** Bandwidth optimization, global delivery
- **Solution:** Adaptive bitrate streaming (HLS), multi-tier CDN

### 4. E-commerce (like Amazon)
- **Scale:** 100M products, 10M orders/day
- **Key Challenge:** Inventory consistency (prevent overselling)
- **Solution:** Pessimistic locking, Saga pattern

### 5. Ride-Sharing (like Uber)
- **Scale:** 10M daily rides
- **Key Challenge:** Real-time driver-rider matching
- **Solution:** Geospatial indexing (Redis GEORADIUS)

### 6. Messaging (like WhatsApp)
- **Scale:** 2B users, 100B messages/day
- **Key Challenge:** Message delivery guarantees
- **Solution:** WebSocket connections, message queues, Cassandra

---

## 🗺️ Content Map

### Section 1: URL Shortener (~8 KB)
- Base62 encoding for short codes
- Database schema
- Caching strategy (Redis)
- Analytics tracking

### Section 2: Social Media Feed (~10 KB)
- Fan-out on write vs fan-out on read
- Hybrid approach (Twitter's actual solution)
- Timeline caching
- Graph structure (follows table)

### Section 3: Video Streaming (~10 KB)
- Video processing pipeline
- Adaptive bitrate streaming (HLS)
- Multi-tier CDN architecture
- Storage optimization

### Section 4: E-commerce Platform (~10 KB)
- Inventory management (pessimistic locking)
- Order processing Saga
- Product search (Elasticsearch)
- Consistency vs availability trade-offs

### Section 5: Ride-Sharing (~8 KB)
- Geospatial indexing (geohashing)
- Driver-rider matching algorithm
- Real-time location tracking (WebSocket)
- Fare calculation

### Section 6: Messaging System (~8 KB)
- Message delivery guarantees
- Online presence (heartbeat)
- Message storage (Cassandra)
- Push notifications

---

## ✅ Learning Checklist

### System Design Process
- [ ] Understand requirements (functional + non-functional)
- [ ] Calculate capacity estimates
- [ ] Design API contracts
- [ ] Choose appropriate data stores
- [ ] Design for scale
- [ ] Identify bottlenecks
- [ ] Plan for failure scenarios

### Common Patterns
- [ ] Caching (Redis) for read-heavy systems
- [ ] CDN for media delivery
- [ ] Message queues for async processing
- [ ] Sharding for horizontal scaling
- [ ] Replication for high availability
- [ ] Load balancing for distribution
- [ ] Rate limiting for abuse prevention

### Trade-off Analysis
- [ ] Consistency vs Availability
- [ ] Latency vs Throughput
- [ ] Cost vs Performance
- [ ] Simplicity vs Flexibility

---

## 💡 Key Concepts

### Read vs Write Heavy

| System | Type | Strategy |
|--------|------|----------|
| URL Shortener | Read-heavy (100:1) | Aggressive caching |
| Social Feed | Write-heavy | Async fan-out |
| E-commerce | Balanced | Read replicas |

### Consistency Requirements

| System | Critical Data | Consistency | Non-Critical | Consistency |
|--------|---------------|-------------|--------------|-------------|
| E-commerce | Inventory, Payment | Strong | View counts | Eventual |
| Ride-Sharing | Driver location | Eventual | Ride history | Eventual |
| Messaging | Messages | At-least-once | Online status | Best-effort |

### Scalability Techniques

```
URL Shortener:
- Cache short codes in Redis (99% hit rate)
- CDN for global distribution
- Read replicas for redirects

Social Feed:
- Pre-compute timelines (push)
- Lazy load celebrity tweets (pull)
- Cache user timelines in Redis

Video Streaming:
- Multi-tier CDN (edge → regional → origin)
- Adaptive bitrate (HLS/DASH)
- Lifecycle policies (hot → warm → cold storage)
```

---

## 🛠️ Design Exercises

### Exercise 1: Design URL Shortener
**Time:** 60 minutes

Requirements:
- 100M URLs created/month
- 10B redirects/month
- Custom short URLs (optional)
- Analytics (clicks, referrers)

Tasks:
1. Design API
2. Choose database schema
3. Design short code generation
4. Plan caching strategy
5. Calculate storage requirements

### Exercise 2: Design Twitter Timeline
**Time:** 90 minutes

Requirements:
- 500M users
- 100M daily active users
- Celebrities with 50M+ followers
- < 500ms timeline load

Tasks:
1. Compare fan-out strategies
2. Design hybrid approach
3. Plan caching strategy
4. Handle celebrity edge case
5. Design database schema

### Exercise 3: Design Uber Matching
**Time:** 75 minutes

Requirements:
- 10M daily rides
- < 3s driver matching
- Real-time location tracking
- Fare calculation

Tasks:
1. Design geospatial indexing
2. Design matching algorithm
3. Plan real-time updates (WebSocket)
4. Handle edge cases (no drivers)
5. Design database schema

---

## 📊 Technology Choices

### Database Selection

| System | Database | Reason |
|--------|----------|--------|
| URL Shortener | PostgreSQL + Redis | RDBMS for data, Redis for caching |
| Social Feed | PostgreSQL + Redis | Graph structure, timeline caching |
| Video Streaming | Object Storage (S3) | Blob storage, petabyte scale |
| E-commerce | PostgreSQL | ACID transactions, inventory |
| Ride-Sharing | PostgreSQL + Redis | Geo-queries with Redis GEORADIUS |
| Messaging | Cassandra | High write throughput, time-series |

### When to Use Cassandra
- ✅ High write throughput (messages, events)
- ✅ Time-series data
- ✅ Linear scalability needed
- ❌ Complex queries or joins

### When to Use PostgreSQL
- ✅ Complex queries and joins
- ✅ Strong consistency required
- ✅ ACID transactions
- ❌ Extreme write throughput (> 100k/sec)

---

## 🎓 Prerequisites

**Before starting this phase:**
- Completed Phases 1-8
- Understanding of distributed systems concepts
- Database knowledge (SQL, NoSQL)
- Caching strategies
- API design principles

**Recommended order:**
1. Start with simpler systems (URL shortener)
2. Progress to complex systems (ride-sharing)
3. Focus on one system at a time
4. Draw architecture diagrams
5. Calculate capacity estimates

---

## 📈 Progress Tracking

### Estimated Timeline
- **Reading:** 90-120 minutes
- **Design exercises:** 4-5 hours
- **Total:** 5.5-6.5 hours

### Completion Criteria
- [ ] Read all 6 case studies
- [ ] Understand capacity calculations
- [ ] Can explain trade-offs
- [ ] Design 2-3 systems independently
- [ ] Draw architecture diagrams
- [ ] Identify appropriate databases

---

## 🔗 Interview Preparation

### Common Questions
1. Design a URL shortener
2. Design Twitter
3. Design YouTube
4. Design Amazon
5. Design Uber
6. Design WhatsApp

### How to Approach
1. **Clarify requirements** (5 min)
   - Functional requirements
   - Non-functional requirements (scale, latency, availability)

2. **Capacity estimation** (5 min)
   - Users, requests per second
   - Storage, bandwidth

3. **API design** (5 min)
   - Key endpoints
   - Request/response formats

4. **Database design** (10 min)
   - Schema
   - Sharding strategy
   - Indexes

5. **High-level architecture** (15 min)
   - Components
   - Data flow
   - Scaling strategy

6. **Deep dives** (10 min)
   - Bottlenecks
   - Trade-offs
   - Failure scenarios

---

## 📝 Notes

**Token Conservation:**
Do not read this file unless the user explicitly asks about real-world systems, case studies, URL shorteners, Twitter, YouTube, Amazon, Uber, WhatsApp, or system design interviews.
