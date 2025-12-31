# Distributed Systems Fundamentals

## Overview

Distributed systems are computing environments where multiple independent components (nodes, services, processes) work together to achieve a common goal. Unlike monolithic systems that run on a single machine, distributed systems span multiple machines connected over a network.

**Key Characteristics:**
- Multiple autonomous components
- Connected via network communication
- Coordinate to appear as a single coherent system
- Subject to partial failures
- No shared clock or memory

This document covers four fundamental concepts that are essential to understanding distributed systems: CAP Theorem, ACID vs BASE, Network Fallacies, and Consistency Models.

---

## 1. CAP Theorem

### What is CAP Theorem?

The **CAP Theorem** (also called Brewer's Theorem) states that in a distributed system, you can only guarantee **two out of three** properties simultaneously:

- **C**onsistency
- **A**vailability
- **P**artition Tolerance

### The Three Properties Explained

#### Consistency (C)
**Definition:** All nodes see the same data at the same time. Every read receives the most recent write.

**What it means:**
- If you write to node A, immediately reading from node B returns the same value
- All replicas have identical data
- No stale reads

**Example:**
```
User updates profile picture on server A
Immediately queries from server B
Consistency: Gets the NEW picture
No Consistency: Might get OLD picture
```

#### Availability (A)
**Definition:** Every request receives a response (success or failure), without guarantee that it contains the most recent write.

**What it means:**
- System continues to operate even if some nodes fail
- Requests don't timeout or error
- System is responsive

**Example:**
```
Server A goes down
User sends request to server B
Availability: Server B responds (even with potentially stale data)
No Availability: Request fails or times out
```

#### Partition Tolerance (P)
**Definition:** The system continues to operate despite network partitions (arbitrary message loss or failure between nodes).

**What it means:**
- System works even when network splits nodes into isolated groups
- Messages between nodes can be lost or delayed
- Network failures don't bring down the system

**Example:**
```
Network cable cut between datacenter A and B
Servers A and B cannot communicate
Partition Tolerance: Both datacenters continue serving requests
No Partition Tolerance: System fails or becomes inconsistent
```

### The Fundamental Trade-off

**Reality:** Network partitions WILL happen (hardware fails, cables cut, network congestion, etc.)

**Therefore:** In practical distributed systems, **Partition Tolerance is mandatory**

**The Real Choice:** **Consistency vs Availability** when partition occurs

```
When network partition happens, choose:

CP System (Consistency + Partition Tolerance):
- Sacrifice Availability
- Return errors rather than stale data
- Wait for partition to heal
- Example: Banking transactions

AP System (Availability + Partition Tolerance):
- Sacrifice Consistency
- Return potentially stale data
- Stay responsive
- Example: Social media feeds
```

### CAP Theorem Examples

#### CP System: Banking Application

**Scenario:** Transfer $100 from Account A to Account B

```
Normal Operation (no partition):
├── User initiates transfer
├── Master DB: A = $1000, B = $500
├── Write: A = $900, B = $600
├── Replicate to all nodes
├── Read from any node: Consistent
└── ✓ Consistency ✓ Availability ✓ Partition Tolerance

Network Partition Occurs:
├── Datacenter 1 and 2 cannot communicate
├── Cannot ensure both see same data
├── CHOICE: Consistency or Availability?
│
└── CP Choice: Prioritize Consistency
    ├── Reject writes during partition
    ├── Return error: "Service temporarily unavailable"
    ├── Users cannot transfer money
    ├── ✓ Consistency ✓ Partition Tolerance ✗ Availability
    └── When partition heals: Data consistent, no conflicts
```

**Why CP for Banking:**
- Cannot allow inconsistent balances
- Better to be temporarily unavailable than wrong
- Regulatory requirements for accuracy
- Examples: PostgreSQL with synchronous replication, HBase, MongoDB (with specific config)

#### AP System: Social Media News Feed

**Scenario:** User posts a status update

```
Normal Operation (no partition):
├── User posts: "Hello World"
├── Write to datacenter A
├── Replicate to datacenter B (eventually)
├── Users in both regions see post
└── ✓ Consistency ✓ Availability ✓ Partition Tolerance

Network Partition Occurs:
├── Datacenter A and B cannot communicate
├── User in region A posts: "Update A"
├── User in region B posts: "Update B"
├── CHOICE: Consistency or Availability?
│
└── AP Choice: Prioritize Availability
    ├── Both datacenters accept writes
    ├── Region A users see "Update A" first
    ├── Region B users see "Update B" first
    ├── ✓ Availability ✓ Partition Tolerance ✗ Consistency
    └── When partition heals: Merge/reconcile conflicts
```

**Why AP for Social Media:**
- Better to show slightly stale data than be down
- User experience priority: responsiveness
- Eventually consistent is acceptable
- Examples: Cassandra, DynamoDB, Riak

#### CA System: Single-Node Database (Theoretical)

**Note:** True CA systems don't exist in distributed systems because partitions are inevitable.

```
Single Machine Database:
├── No network partition possible (single machine)
├── Consistent: All reads get latest write
├── Available: Always responds
├── ✓ Consistency ✓ Availability ✗ Partition Tolerance
└── Not a distributed system!

Example: SQLite, single PostgreSQL instance
Limitation: No fault tolerance, no scaling
```

### CAP Theorem Nuances

#### It's Not Binary

Modern systems exist on a spectrum:
```
[Strong Consistency] ←──────────→ [High Availability]
        CP Systems                      AP Systems
           ↓                                ↓
    Banking, Finance              Social Media, Caching
    HBase, MongoDB               Cassandra, DynamoDB
```

#### Tunable Consistency

Many systems allow configuring the trade-off:

**Cassandra Example:**
```
Write Consistency Levels:
- ONE: Write to 1 replica (high availability)
- QUORUM: Write to majority (balanced)
- ALL: Write to all replicas (strong consistency)

Read Consistency Levels:
- ONE: Read from 1 replica (fast, might be stale)
- QUORUM: Read from majority (balanced)
- ALL: Read from all replicas (consistent but slow)

Strong Consistency: Write(QUORUM) + Read(QUORUM)
High Availability: Write(ONE) + Read(ONE)
```

#### Partition is Rare

During normal operation (no partition):
- System can be BOTH consistent AND available
- CAP trade-off only matters DURING partition
- Well-designed systems minimize partition impact

### Real-World CAP Decisions

#### Google Spanner: Circumventing CAP?

**Claim:** Provides both consistency and availability

**Reality:**
- Uses atomic clocks and GPS
- Guarantees globally consistent timestamps
- Makes partition windows extremely small (milliseconds)
- Still sacrifices availability during actual partitions
- **Doesn't violate CAP, just minimizes partition impact**

#### Amazon DynamoDB: AP with Dial

**Design:**
- Primarily AP (highly available)
- Eventually consistent by default
- Offers optional strong consistency for reads
- Trade-off: Strong reads are slower and may be unavailable

```
DynamoDB Operations:

Eventually Consistent Read (AP):
├── Fast (single node)
├── May return stale data
└── Always available

Strongly Consistent Read (CP-like):
├── Slower (waits for latest)
├── May fail during partition
└── Returns latest data
```

### Visualizing CAP

```
         Consistency
              /\
             /  \
            /    \
           /  CA  \
          /  (Not  \
         /  practical) \
        /______________\
       /\              /\
      /  \            /  \
     /    \          /    \
    /  CP  \        /  AP  \
   / (Choose \    / (Choose \
  /Consistency)\  /Availability)\
 /______________\/______________\
Partition         Availability
Tolerance

REALITY: P is mandatory
CHOICE: C or A during partition
```

---

## 2. ACID vs BASE

Distributed systems require different approaches to data consistency compared to traditional databases. ACID and BASE represent two different philosophies.

### ACID: Traditional Database Guarantees

**ACID** is the gold standard for traditional relational databases, emphasizing strong consistency and reliability.

#### Atomicity (A)

**Definition:** A transaction is all-or-nothing. Either all operations succeed, or none do.

**Example:**
```sql
BEGIN TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

Success: Both updates happen
Failure: Neither update happens (rollback)
No partial state: Never have only one update
```

**Real-World:**
```
Bank Transfer:
├── Deduct from Account A
├── Credit to Account B
├── Update transaction log
│
If power outage occurs mid-transaction:
└── Atomicity: All changes rolled back
    Result: No money lost or created
```

#### Consistency (C)

**Definition:** Transaction brings database from one valid state to another valid state. All rules, constraints, and triggers are enforced.

**Example:**
```sql
Rule: Account balance cannot be negative

Transaction attempt:
UPDATE accounts SET balance = balance - 1000
WHERE id = 1 AND balance = 500;

Consistency: Transaction rejected (would violate rule)
Database remains in valid state
```

**Real-World:**
```
E-commerce Inventory:
Rule: Stock cannot be negative

Attempt to sell 100 items when only 50 in stock:
└── Consistency: Transaction rejected
    Result: Database rules enforced
```

#### Isolation (I)

**Definition:** Concurrent transactions don't interfere with each other. Intermediate states of a transaction are invisible to other transactions.

**Example:**
```
Transaction A: Transfer $100 (A→B)
Transaction B: Calculate total balance

Without Isolation:
├── A reads: Account A = $1000, B = $500
├── A deducts: Account A = $900 (not committed)
├── B reads: Account A = $900, B = $500 (WRONG!)
├── A credits: Account B = $600 (commits)
└── B calculated total = $1400 (should be $1500)

With Isolation:
├── A reads: Account A = $1000, B = $500
├── A deducts: Account A = $900 (locked)
├── B reads: Waits or sees $1000/$500 (before A)
├── A credits: Account B = $600 (commits)
└── B reads: Account A = $900, B = $600 (CORRECT)
```

**Isolation Levels:**
```
Strongest to Weakest:

1. Serializable (strictest)
   - Transactions execute as if serial
   - No concurrency anomalies
   - Slowest

2. Repeatable Read
   - Prevents dirty reads and non-repeatable reads
   - Can have phantom reads

3. Read Committed
   - Only see committed data
   - Can have non-repeatable reads

4. Read Uncommitted (weakest)
   - Can see uncommitted changes (dirty reads)
   - Fastest but dangerous
```

#### Durability (D)

**Definition:** Once transaction commits, changes are permanent (survive system crashes, power outages).

**Example:**
```
User completes purchase:
├── Transaction commits
├── Database returns success
├── Server crashes 1 second later
│
Durability: Purchase is saved
└── When server restarts: Purchase still exists
```

**Implementation:**
- Write-Ahead Logging (WAL)
- Disk persistence before commit
- Replication to multiple nodes

### BASE: Distributed Systems Philosophy

**BASE** is an approach designed for distributed systems, emphasizing availability over consistency.

**BASE stands for:**
- **B**asically **A**vailable
- **S**oft state
- **E**ventual consistency

#### Basically Available

**Definition:** System is available most of the time, though it may return partial or degraded results.

**Example:**
```
E-commerce during Black Friday:
├── Main product DB overloaded
├── Option 1 (ACID): Return error, site down
├── Option 2 (BASE): Return cached product data
│
BASE Choice: Show slightly stale data
└── Better to show yesterday's price than crash
```

**Real-World:**
```
Amazon Product Page:
├── Product details: From cache (may be stale)
├── Reviews: From separate service (may lag)
├── Inventory: From warehouse (best effort)
├── Recommendations: From ML service (fallback to generic)
│
If one component fails:
└── Show partial page, not error
    Result: Degraded but functional
```

#### Soft State

**Definition:** System state may change over time, even without new input, due to eventual consistency.

**Example:**
```
User posts comment:
├── Written to datacenter A
├── User immediately reads from datacenter B
├── Comment not yet replicated to B
├── User sees: No comment (soft state)
├── Wait 100ms: Replication completes
└── User sees: Comment appears (state changed without new write)
```

**Real-World:**
```
Social Media "Like" Counter:
├── 10:00:00 - Counter shows: 42 likes
├── 10:00:01 - User likes (written to DC1)
├── 10:00:02 - Counter shows: 42 (from DC2 cache)
├── 10:00:03 - Counter shows: 43 (replication caught up)
├── 10:00:04 - Counter shows: 46 (other likes replicated)
│
State changes without user action (soft state)
└── Eventually settles to correct value
```

#### Eventual Consistency

**Definition:** If no new updates are made, eventually all replicas will converge to the same value.

**Example:**
```
Document Collaboration (like Google Docs):
├── User A (NYC) types: "Hello"
├── User B (London) types: "World"
├── Both typing simultaneously
│
Immediate State:
├── NYC datacenter: "Hello"
├── London datacenter: "World"
├── Inconsistent!
│
After replication (seconds later):
├── NYC datacenter: "HelloWorld" (or "WorldHello")
├── London datacenter: "HelloWorld" (or "WorldHello")
└── Eventually consistent
```

### ACID vs BASE Comparison

#### Philosophy

```
ACID: "Better to fail than be wrong"
BASE: "Better to work partially than not at all"

ACID: Strong guarantees, may sacrifice availability
BASE: High availability, eventual correctness
```

#### Use Case Suitability

```
ACID Systems:
├── Banking transactions
├── Order processing
├── Financial trading
├── Medical records
├── Regulatory compliance
└── Anywhere correctness > availability

BASE Systems:
├── Social media feeds
├── Product catalogs
├── DNS systems
├── Caching layers
├── Analytics dashboards
└── Anywhere availability > instant correctness
```

#### Implementation Examples

**ACID Databases:**
- PostgreSQL
- MySQL (InnoDB engine)
- Oracle Database
- SQL Server
- CockroachDB (distributed ACID)

**BASE Systems:**
- Cassandra
- DynamoDB
- Riak
- Couchbase
- MongoDB (configurable)

### Real-World Scenario: E-commerce Platform

#### ACID Approach (Traditional)

```
User Checkout Flow:
├── BEGIN TRANSACTION
├── Check inventory
├── Reserve items
├── Process payment
├── Deduct inventory
├── Create order
├── COMMIT TRANSACTION
│
Guarantees:
├── ✓ Payment and inventory always in sync
├── ✓ No overselling
├── ✓ Audit trail accurate
│
Trade-offs:
├── ✗ Single point of failure (database)
├── ✗ Slower during high traffic
├── ✗ May reject orders when system stressed
└── ✗ Difficult to scale globally
```

#### BASE Approach (Distributed)

```
User Checkout Flow:
├── Check inventory (from cache, might be stale)
├── Optimistically reserve items (local datacenter)
├── Process payment (asynchronous)
├── Queue inventory deduction
├── Return success to user
├── Background: Reconcile inventory across datacenters
│
Guarantees:
├── ✓ Always accepts orders (high availability)
├── ✓ Fast response to user
├── ✓ Scales globally
│
Trade-offs:
├── ✗ Might accept order when out of stock (rare)
├── ✗ Inventory count may be slightly off
├── ✗ Must handle conflicts (e.g., overselling)
└── ✗ Complex reconciliation logic

Conflict Resolution:
├── If oversold: Backorder or cancel last orders
├── Send apology email
├── Compensating action (refund, discount)
└── Eventually correct inventory
```

### Hybrid Approaches

Many modern systems combine both:

#### Example: Netflix

```
ACID for:
├── Billing (must be accurate)
├── Subscriptions
└── Payment processing

BASE for:
├── Movie recommendations (eventual is fine)
├── Watch history replication
├── Content delivery
└── User activity logs
```

#### Example: Uber

```
ACID for:
├── Payment processing
├── Trip fares
└── Driver earnings

BASE for:
├── Driver location updates (real-time, approximate ok)
├── Surge pricing calculations (eventual)
├── Trip history
└── Ratings and reviews
```

---

## 3. Network Fallacies

The **Eight Fallacies of Distributed Computing** are assumptions programmers often make about networks, all of which are false. Understanding these helps build robust distributed systems.

### Historical Context

**Coined by:** L. Peter Deutsch and others at Sun Microsystems (1990s)

**Why it matters:** Many distributed system failures occur because developers assumed these fallacies were true.

### The Eight Fallacies

#### Fallacy 1: The Network is Reliable

**The Assumption:** Networks don't fail; packets always reach their destination.

**The Reality:** Networks fail constantly in various ways.

**Failures:**
```
- Packet loss (congestion, buffer overflow)
- Network partitions (cable cuts, switch failures)
- Intermittent connectivity (Wi-Fi, mobile networks)
- Hardware failures (routers, NICs)
- Software bugs (firewall misconfig, DNS issues)
```

**Real-World Example:**
```
Microservice A calls B:
A: "Transfer $1000 from account 123"
├── Network glitch: Packet lost
├── A doesn't receive response
├── A's timeout: 30 seconds
│
Questions:
├── Did B receive the request?
├── Did B process it?
├── Did the response get lost?
├── Should A retry? (might duplicate transfer!)
└── How to handle this?

Solution Patterns:
├── Idempotency (safe to retry)
├── Request IDs (detect duplicates)
├── Timeouts and circuit breakers
└── Compensating transactions
```

#### Fallacy 2: Latency is Zero

**The Assumption:** Network calls are instant like in-memory function calls.

**The Reality:** Network latency is significant and variable.

**Latency Examples:**
```
Operation Latency:
├── L1 cache reference: 0.5 ns
├── Main memory reference: 100 ns
├── Same datacenter network: 0.5 ms (1,000,000× slower than L1)
├── Cross-country network: 50 ms (100,000,000× slower)
└── Intercontinental: 150 ms

Function call: Nanoseconds
Network call: Milliseconds (1,000,000× difference!)
```

**Real-World Impact:**
```
Monolith (in-process):
getUserProfile() → 0.001 ms
getOrders() → 0.001 ms
getRecommendations() → 0.001 ms
Total: 0.003 ms

Microservices (network calls):
HTTP GET /users/123 → 5 ms
HTTP GET /orders?user=123 → 5 ms
HTTP GET /recommendations/123 → 5 ms
Total: 15 ms (5,000× slower)

Lesson: Minimize network calls, use batching, caching
```

**The N+1 Problem:**
```
Bad Design:
for user in users:  # 1000 users
    profile = http.get(f"/users/{user.id}")  # 1000 network calls
    display(profile)

Total time: 1000 × 5ms = 5 seconds

Good Design:
profiles = http.post("/users/batch", user_ids)  # 1 network call
Total time: 1 × 50ms = 50 milliseconds (100× faster)
```

#### Fallacy 3: Bandwidth is Infinite

**The Assumption:** You can send as much data as you want over the network.

**The Reality:** Bandwidth is limited and costly.

**Constraints:**
```
Network Bandwidth Limits:
├── Home Internet: 100 Mbps - 1 Gbps
├── Corporate LAN: 1 Gbps - 10 Gbps
├── Datacenter: 10 Gbps - 100 Gbps
├── Cloud region-to-region: Variable, expensive
└── Shared with other traffic
```

**Real-World Example:**
```
API Design Problem:

Bad: Return entire user object with everything
{
  "id": 123,
  "name": "Alice",
  "profile_picture": "<base64 encoded 2MB image>",
  "all_orders": [/* 10,000 orders */],
  "full_activity_log": [/* 1,000,000 events */],
  "connections": [/* 5,000 friends with full data */]
}
Response size: 50 MB per user
100 users: 5 GB of bandwidth

Good: Return minimal data + pagination
{
  "id": 123,
  "name": "Alice",
  "profile_picture_url": "https://cdn.../pic.jpg",
  "recent_orders_url": "/api/users/123/orders?limit=10"
}
Response size: 1 KB per user
100 users: 100 KB of bandwidth (50,000× improvement)
```

#### Fallacy 4: The Network is Secure

**The Assumption:** Networks are safe; data can't be intercepted or tampered with.

**The Reality:** Networks are hostile environments.

**Threats:**
```
- Man-in-the-middle attacks
- Packet sniffing
- DNS spoofing
- DDoS attacks
- Credential theft
- Data interception
```

**Real-World Example:**
```
Microservice A → B communication:

Insecure (assumes Fallacy 4):
http://internal-service/api/users
├── Unencrypted traffic
├── No authentication
├── Trust network security
└── Risk: If attacker gets inside network, full access

Secure (assumes network is hostile):
https://internal-service/api/users
├── TLS encryption (even internally)
├── Mutual TLS (mTLS) for service authentication
├── API keys or OAuth tokens
├── Network segmentation
└── Defense in depth
```

#### Fallacy 5: Topology Doesn't Change

**The Assumption:** Network structure is static; services are always in the same place.

**The Reality:** Network topology is dynamic.

**Changes:**
```
- Servers auto-scale up/down
- Containers move between hosts
- Deployments change IP addresses
- Load balancers added/removed
- Datacenters go offline
- Cloud providers migrate instances
```

**Real-World Example:**
```
Hardcoded Service Discovery (assumes static):
DATABASE_URL = "192.168.1.100:5432"
CACHE_URL = "192.168.1.101:6379"

Problems:
├── Server 192.168.1.100 restarts: New IP
├── Database scaled: Which IP to use?
├── Failover to backup: Hardcoded IP wrong
└── Cannot deploy without code change

Dynamic Service Discovery (handles change):
database = consul.discover("postgres")
cache = consul.discover("redis")

Benefits:
├── Services register themselves
├── Health checks remove unhealthy instances
├── Automatic failover
└── Scales elastically
```

#### Fallacy 6: There is One Administrator

**The Assumption:** One person/team controls the entire network.

**The Reality:** Multiple teams, organizations, and providers manage different parts.

**Reality:**
```
Your E-commerce Architecture:
├── Your services: Your team
├── Load balancer: Infrastructure team
├── Corporate network: Network team
├── Internet provider: ISP
├── CDN: Cloudflare/Akamai
├── Cloud provider: AWS/Azure/GCP
├── Payment gateway: Stripe/PayPal
└── Shipping API: FedEx/UPS

Each has different:
├── Maintenance windows
├── Outage schedules
├── Security policies
├── Configuration standards
└── Priorities
```

**Real-World Impact:**
```
Deployment Planning:
├── You deploy at 2 AM (low traffic)
├── But: Cloud provider scheduled maintenance at 2 AM
├── And: ISP doing infrastructure upgrade at 2 AM
├── Result: Multiple points of failure during your deploy
│
Need to:
├── Communicate with all stakeholders
├── Monitor external dependencies
├── Have rollback plans
└── Can't assume control over everything
```

#### Fallacy 7: Transport Cost is Zero

**The Assumption:** Sending data over network is free.

**The Reality:** Network usage has real monetary and performance costs.

**Costs:**
```
Monetary Costs:
├── Cloud egress fees: $0.05 - $0.12 per GB
├── Cross-region transfer: $0.02 per GB
├── CDN bandwidth: $0.08 per GB
└── Example: 1 TB/day = $3,600/month

Performance Costs:
├── CPU to serialize/deserialize
├── Memory for buffering
├── Network card processing
├── Encryption/decryption overhead
└── Battery drain (mobile)
```

**Real-World Example:**
```
Video Streaming Service:

Naive Design:
├── All video served from central datacenter
├── 1 million users × 2 GB/day
├── 2 PB (petabytes) per day
├── Cost: 2,000,000 GB × $0.09 = $180,000/day
└── $5.4 million/month in bandwidth!

Optimized Design:
├── CDN caching (90% cache hit rate)
├── Regional datacenters
├── Peer-to-peer for live streams
├── Adaptive bitrate (lower quality when needed)
└── Cost: $500,000/month (10× savings)
```

#### Fallacy 8: The Network is Homogeneous

**The Assumption:** All network equipment and protocols are the same.

**The Reality:** Networks are heterogeneous (mixed technologies).

**Heterogeneity:**
```
Your request path:
├── Mobile device: 4G/5G/WiFi
├── ISP: Fiber/cable/DSL
├── CDN: Anycast routing
├── Load balancer: Layer 7 HTTP
├── Internal network: Layer 4 TCP
├── Service mesh: gRPC
└── Database: Custom protocol

Each has different:
├── Protocols (HTTP, TCP, UDP, gRPC, etc.)
├── Message sizes limits
├── Timeout behaviors
├── Error handling
├── Performance characteristics
└── Capabilities
```

**Real-World Example:**
```
API Design Problem:

Assumption: All clients are modern browsers

Reality:
├── iOS app (HTTP/2, binary protocol)
├── Android app (HTTP/1.1, JSON)
├── Legacy partner (SOAP/XML)
├── Internal services (gRPC)
├── Webhook consumers (HTTP/1.1, timeouts after 5s)
└── Mobile browsers (slow connections, small payloads)

Design considerations:
├── Content negotiation (JSON vs XML vs Protocol Buffers)
├── Compression (gzip, brotli)
├── Versioning (backward compatibility)
├── Timeout handling (vary by client)
└── Payload size (optimize for mobile)
```

### Designing for Fallacies

**Principles to counter fallacies:**

```
1. Assume failure (Fallacy 1)
   - Implement retries with exponential backoff
   - Use circuit breakers
   - Design for graceful degradation

2. Minimize latency (Fallacy 2)
   - Batch operations
   - Cache aggressively
   - Use async communication where possible

3. Optimize bandwidth (Fallacy 3)
   - Compress data
   - Paginate results
   - Use efficient serialization (Protocol Buffers vs JSON)

4. Secure everything (Fallacy 4)
   - TLS/mTLS everywhere
   - Authenticate and authorize
   - Encrypt sensitive data

5. Service discovery (Fallacy 5)
   - Use service registry (Consul, Eureka)
   - Health checks
   - Dynamic configuration

6. Design for multi-tenancy (Fallacy 6)
   - Don't assume control
   - Monitor external dependencies
   - Have SLAs with vendors

7. Monitor costs (Fallacy 7)
   - Track bandwidth usage
   - Optimize expensive paths
   - Consider cost in architecture decisions

8. Abstract protocols (Fallacy 8)
   - API versioning
   - Content negotiation
   - Protocol adapters
```

---

## 4. Consistency Models

In distributed systems, **consistency** defines what guarantee the system provides about the order and visibility of operations across multiple replicas.

### Why Consistency Models Matter

```
Scenario: User updates profile picture

Question: When do other users see the new picture?

Answers (depending on consistency model):
├── Immediately, guaranteed (Strong Consistency)
├── Within 1 second (Bounded Staleness)
├── Eventually, no guarantee when (Eventual Consistency)
├── Depends on which datacenter you read from (Causal Consistency)
└── Maybe never, if you always read from stale replica (No Consistency)
```

**The Fundamental Trade-off:**
- **Stronger Consistency**: More guarantees, slower, less available
- **Weaker Consistency**: Fewer guarantees, faster, more available

### Consistency Spectrum

```
[Strongest] ←────────────────────────→ [Weakest]
    ↓                                        ↓
Linearizable → Sequential → Causal → Eventual → No Consistency
    ↓              ↓          ↓          ↓           ↓
 Slowest       Moderate   Balanced    Fast      Fastest
Most Available                            Least Available
```

### Strong Consistency

#### Linearizability (Strongest)

**Definition:** Operations appear to occur instantaneously at some point between invocation and completion. Once a write completes, all subsequent reads see that write.

**Guarantee:**
```
Time: ─────→
Write(X=1) completes at T1
Any Read(X) after T1 returns 1 (guaranteed)
```

**Example:**
```
User A: Write(profile="new.jpg") → Success at 10:00:00
User B: Read(profile) at 10:00:01 → Must return "new.jpg"
User C: Read(profile) at 10:00:02 → Must return "new.jpg"

No user can see old value after write completes
```

**Implementation:**
- Synchronous replication to all replicas
- Consensus algorithms (Paxos, Raft)
- Two-phase commit

**Use Cases:**
- Banking transactions
- Inventory management
- Lock services (ZooKeeper, etcd)

**Trade-offs:**
- ✓ Simplest programming model (like single machine)
- ✗ Slowest (wait for all replicas)
- ✗ Less available (fails if replicas down)

#### Sequential Consistency

**Definition:** Operations appear to execute in some sequential order, and all nodes see the same order.

**Difference from Linearizability:** No real-time guarantee (operations may appear to reorder in time)

**Example:**
```
Real-time order:
Node A: Write(X=1) at 10:00:00
Node B: Write(X=2) at 10:00:01
Node C: Write(X=3) at 10:00:02

Linearizable: All nodes must see: X=1, then X=2, then X=3

Sequential: All nodes must see SAME order, but could be:
├── Option 1: X=1, X=2, X=3 (respects time)
├── Option 2: X=2, X=1, X=3 (reordered, but all nodes agree)
└── Not allowed: Node A sees X=1,X=2,X=3 but Node B sees X=2,X=3,X=1
```

### Causal Consistency

**Definition:** Operations that are causally related must be seen in the same order by all nodes. Concurrent operations may be seen in different orders.

**Causal Relationships:**
```
Causally Related (must preserve order):
├── Write then Read (read depends on write)
├── Read then Write (write depends on read)
└── Transitive: A→B and B→C means A→C

Concurrent (can reorder):
└── Operations without dependency
```

**Example: Social Media Comments**
```
Timeline:
Alice: Posts "What's your favorite color?" (Event A)
Bob: Reads Alice's post, replies "Blue" (Event B, depends on A)
Carol: Reads Bob's reply, replies "Me too!" (Event C, depends on B)
Dave: Posts "Hello" (Event D, concurrent with all above)

Causal Consistency Guarantees:
├── Everyone sees: A before B before C (causally related)
├── D can appear anywhere (concurrent)
│
Valid Orders:
├── D, A, B, C
├── A, D, B, C
├── A, B, D, C
├── A, B, C, D
│
Invalid Orders:
├── B, A, C (B depends on A, must come after)
└── A, C, B (C depends on B, must come after)
```

**Use Cases:**
- Social media feeds
- Collaborative editing
- Distributed databases (Cassandra with causal consistency)

**Trade-offs:**
- ✓ More performant than strong consistency
- ✓ Intuitive for humans (preserves cause-effect)
- ✗ More complex to implement
- ✗ Still requires some coordination

### Eventual Consistency

**Definition:** If no new updates are made, eventually all replicas will converge to the same value. No guarantee on timing.

**Guarantee:**
```
Write(X=1) at T0
Read(X) at T1 → might return old value
Read(X) at T2 → might return old value
Read(X) at T3 → might return old value
...
Read(X) at T∞ → returns 1 (eventually)

"Eventually" could be milliseconds or minutes
```

**Example: DNS**
```
Update DNS Record:
├── example.com → 192.168.1.1 (old)
├── Change to: example.com → 192.168.1.2 (new)
│
Propagation:
├── Primary server: Updated immediately
├── Secondary servers: Updated in 1-60 minutes (TTL)
├── Your computer cache: Updated in hours
│
Result: Different users see different IPs for hours
Eventually: All see 192.168.1.2
```

**Conflict Resolution:**

When multiple writes happen concurrently:

```
Last-Write-Wins (LWW):
├── Use timestamp to determine winner
├── Simple but may lose data
Example: X=1 at 10:00:00, X=2 at 10:00:01 → X=2 wins

Version Vectors:
├── Track causality with version numbers
├── Detect conflicts, application resolves
Example: Shopping cart merge (keep all items)

CRDTs (Conflict-Free Replicated Data Types):
├── Mathematically guaranteed to converge
├── Examples: Counters, Sets, Maps
Example: Like counter (increment is commutative)
```

**Use Cases:**
- Caching systems (Redis, Memcached)
- DNS
- Session storage
- Analytics data
- Social media likes/views counts

**Trade-offs:**
- ✓ Highly available
- ✓ Very fast (no coordination)
- ✓ Partition tolerant
- ✗ Application must handle stale data
- ✗ Possible conflicts

### Monotonic Reads

**Definition:** If a process reads X=1, it will never subsequently read an older value.

**Example:**
```
Session Consistency (Shopping Cart):

User adds item 1: Cart = [1]
User adds item 2: Cart = [1, 2]
User adds item 3: Cart = [1, 2, 3]

Monotonic Reads: User never sees [1, 2] after seeing [1, 2, 3]

Implementation: Sticky sessions (always route user to same replica)
```

### Read-Your-Writes Consistency

**Definition:** A process always sees its own writes.

**Example:**
```
User posts comment "Hello":
├── Write to datacenter A
├── User immediately refreshes page
├── Read might go to datacenter B (not yet replicated)
│
Without Read-Your-Writes:
└── User doesn't see own comment (bad UX)

With Read-Your-Writes:
└── User always sees own comment (route user's reads to A)
```

### Bounded Staleness

**Definition:** Reads may lag behind writes, but by a bounded amount (time or version).

**Example:**
```
Azure Cosmos DB Bounded Staleness:
├── Configuration: Max staleness = 10 seconds
├── Guarantee: Reads are at most 10 seconds old
│
User writes at 10:00:00
User reads at 10:00:05 → Might see old value
User reads at 10:00:11 → Guaranteed to see new value (bounded)
```

**Use Cases:**
- Geo-replicated databases
- Read-heavy workloads with acceptable lag
- Leaderboards, counts (approximate ok)

### Consistency in Practice: Examples

#### DynamoDB

```
Default: Eventual Consistency
├── Fast reads
├── May return stale data
├── Cheap

Optional: Strong Consistency
├── Slower reads
├── Always latest data
├── More expensive
└── May be unavailable during partition

Choice per read request
```

#### MongoDB

```
Default: Eventual Consistency (reads from secondaries)

Write Concern:
├── w:1 (write to primary only)
├── w:majority (write to majority of replicas)
└── w:all (write to all replicas)

Read Concern:
├── local (read from primary, might be uncommitted)
├── majority (read committed by majority)
└── linearizable (strongest)

Tunable consistency per operation
```

#### Cassandra

```
Tunable Consistency:

Write Consistency Level:
├── ANY (write to at least one node)
├── ONE (write to one replica)
├── QUORUM (write to majority)
├── ALL (write to all replicas)

Read Consistency Level:
├── ONE (read from one replica)
├── QUORUM (read from majority)
├── ALL (read from all replicas)

Strong Consistency: Write(QUORUM) + Read(QUORUM)
Eventual Consistency: Write(ONE) + Read(ONE)
```

---

## Putting It All Together

### The Distributed Systems Triangle

All four fundamentals are interconnected:

```
CAP Theorem: Defines constraints (C, A, P)
     ↓
ACID vs BASE: Philosophical approaches
     ↓
Network Fallacies: Practical realities
     ↓
Consistency Models: Specific implementations
```

### Decision Framework

When designing a distributed system:

```
1. Identify Requirements
   ├── Critical consistency needs? → Strong consistency
   ├── Need high availability? → Eventual consistency
   ├── Global distribution? → Consider CAP implications
   └── Budget constraints? → Factor network costs

2. Choose Consistency Model
   ├── Banking → Linearizable (ACID)
   ├── Social media → Eventual (BASE)
   ├── Shopping cart → Causal or Read-Your-Writes
   └── DNS → Eventual

3. Design for Network Realities
   ├── Assume unreliable network (Fallacy 1)
   ├── Minimize round trips (Fallacy 2)
   ├── Optimize bandwidth (Fallacy 3)
   └── Handle all 8 fallacies

4. Select CAP Trade-off
   ├── CP system (consistency over availability)
   └── AP system (availability over consistency)
```

### Example: E-commerce System

```
Different subsystems, different consistency:

Product Catalog (AP, Eventual):
├── High availability critical
├── Slight staleness acceptable
├── Many reads, few writes
└── Use: Cassandra with eventual consistency

Inventory (CP, Strong):
├── Cannot oversell
├── Accuracy over availability
├── Critical consistency
└── Use: PostgreSQL with serializable isolation

Shopping Cart (Session, Causal):
├── User must see own changes
├── Eventual replication acceptable
├── Sticky sessions
└── Use: Redis with read-your-writes

Payment (ACID, Linearizable):
├── Absolute correctness required
├── Cannot lose money
├── Regulatory compliance
└── Use: PostgreSQL with two-phase commit
```

---

## Summary

### Key Takeaways

1. **CAP Theorem**
   - Can only have 2 of 3: Consistency, Availability, Partition Tolerance
   - Partitions are inevitable → Choose between C and A
   - Not binary, exists on spectrum

2. **ACID vs BASE**
   - ACID: Strong guarantees, traditional databases
   - BASE: High availability, distributed systems
   - Choose based on use case
   - Can mix both in same system

3. **Network Fallacies**
   - Networks are unreliable, have latency, limited bandwidth
   - Security cannot be assumed
   - Topology changes, multiple administrators
   - Design defensively

4. **Consistency Models**
   - Range from strong (linearizable) to weak (eventual)
   - Stronger = slower but simpler programming
   - Weaker = faster but must handle complexity
   - Choose based on requirements

### Next Steps

With these fundamentals understood, you're ready to learn:
- **System Design Principles** (next document)
- Microservices architecture patterns
- Distributed databases deep dive
- Service discovery and coordination
- Failure handling and resilience patterns

---

## Further Reading

### Books
- "Designing Data-Intensive Applications" by Martin Kleppmann (Chapters 5-9)
- "Distributed Systems: Principles and Paradigms" by Tanenbaum & Van Steen
- "Database Internals" by Alex Petrov

### Papers
- "Brewer's CAP Theorem" (Eric Brewer, 2000)
- "Eventually Consistent" (Werner Vogels, Amazon CTO)
- "Fallacies of Distributed Computing Explained" (Arnon Rotem-Gal-Oz)
- "Consistency in Non-Transactional Distributed Storage Systems" (Survey paper)

### Online Resources
- Jepsen.io (distributed systems testing)
- Martin Kleppmann's blog
- AWS Architecture Blog
- Google Cloud Architecture Center

---

**Remember:** These are fundamentals, not rules. Real systems often make pragmatic trade-offs based on specific requirements, constraints, and use cases. Understanding these concepts helps you make informed decisions.
