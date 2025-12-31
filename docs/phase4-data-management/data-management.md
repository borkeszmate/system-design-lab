# Data Management in Distributed Systems

## Overview

Data management in distributed systems involves choosing appropriate storage solutions, ensuring consistency across nodes, and handling replication. Unlike monolithic systems with a single database, distributed systems must carefully design how data is stored, accessed, and kept consistent.

**Key Topics:**
1. **Database Types & Use Cases** - Choose the right database for each need
2. **Data Consistency Patterns** - Ensure correctness across distributed data
3. **Data Replication** - Keep data available and durable

---

## 1. Database Types & Use Cases

### Polyglot Persistence

**Definition:** Using different database technologies for different data storage needs within the same application.

**Why:** One size doesn't fit all - different data has different access patterns and requirements.

```
E-commerce Application:
├── User Sessions → Redis (key-value)
├── User Profiles → MongoDB (document)
├── Product Catalog → Elasticsearch (search)
├── Orders → PostgreSQL (relational)
├── Social Graph → Neo4j (graph)
└── Metrics → InfluxDB (time-series)
```

### Relational Databases (SQL)

**Examples:** PostgreSQL, MySQL, Oracle, SQL Server

**Strengths:**
- ACID transactions
- Complex queries with JOINs
- Data integrity (foreign keys, constraints)
- Mature ecosystem

**Use Cases:**
```
✓ Financial transactions (strict consistency)
✓ Order processing (referential integrity)
✓ User management (relationships between entities)
✓ Inventory tracking (atomic updates)
```

**When NOT to use:**
```
✗ Unstructured data (varying schemas)
✗ Massive scale (billions of rows, complex sharding)
✗ Need flexible schema evolution
✗ Graph relationships (many-to-many)
```

**Example: Order System**
```sql
-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    total DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Order items with foreign key
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id),
    quantity INT,
    price DECIMAL(10,2)
);

-- Complex query with JOINs
SELECT 
    o.id,
    u.email,
    SUM(oi.quantity * oi.price) as total
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON o.order_id = oi.id
WHERE o.created_at > NOW() - INTERVAL '30 days'
GROUP BY o.id, u.email;
```

---

### Document Databases (NoSQL)

**Examples:** MongoDB, CouchDB, DynamoDB (also key-value)

**Strengths:**
- Flexible schema (JSON documents)
- Easy to scale horizontally
- Natural fit for object-oriented programming
- Fast reads for denormalized data

**Use Cases:**
```
✓ Product catalogs (varying attributes)
✓ Content management (blog posts, articles)
✓ User profiles (different user types)
✓ Event logging (varied event structures)
```

**Example: Product Catalog (MongoDB)**
```javascript
// Different products with different fields
{
  "_id": "prod_123",
  "name": "Laptop",
  "category": "electronics",
  "price": 999.99,
  "specs": {
    "cpu": "Intel i7",
    "ram": "16GB",
    "storage": "512GB SSD"
  },
  "reviews": [
    {"user": "alice", "rating": 5, "comment": "Great!"}
  ]
}

{
  "_id": "prod_456",
  "name": "T-Shirt",
  "category": "clothing",
  "price": 19.99,
  "sizes": ["S", "M", "L", "XL"],
  "color": "blue"
  // Different schema - no problem!
}

// Query products
db.products.find({
  "category": "electronics",
  "price": { $lt: 1000 }
}).sort({ price: -1 });
```

---

### Key-Value Stores

**Examples:** Redis, Memcached, DynamoDB, Riak

**Strengths:**
- Extremely fast (in-memory)
- Simple data model (key → value)
- Horizontal scalability
- Low latency

**Use Cases:**
```
✓ Session storage
✓ Caching
✓ Rate limiting
✓ Real-time leaderboards
✓ Feature flags
```

**Example: Session Store (Redis)**
```python
import redis
import json

cache = redis.Redis()

# Store session
session_data = {
    "user_id": 123,
    "username": "alice",
    "roles": ["user", "premium"]
}
cache.setex(
    f"session:abc123",
    3600,  # TTL: 1 hour
    json.dumps(session_data)
)

# Retrieve session
session = cache.get("session:abc123")
if session:
    data = json.loads(session)
    print(data["username"])  # alice
```

---

### Column-Family Databases

**Examples:** Cassandra, HBase, ScyllaDB

**Strengths:**
- Massive scale (petabytes)
- High write throughput
- Time-series data
- Tunable consistency

**Use Cases:**
```
✓ Time-series data (IoT sensors, logs)
✓ Messaging systems (message history)
✓ Analytics (large dataset processing)
✓ Event tracking (clickstream data)
```

**Example: IoT Sensor Data (Cassandra)**
```cql
CREATE TABLE sensor_readings (
    sensor_id text,
    timestamp timestamp,
    temperature decimal,
    humidity decimal,
    PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Insert millions of readings efficiently
INSERT INTO sensor_readings (sensor_id, timestamp, temperature, humidity)
VALUES ('sensor_001', '2024-01-15 10:30:00', 23.5, 45.2);

-- Query recent readings for a sensor
SELECT * FROM sensor_readings
WHERE sensor_id = 'sensor_001'
AND timestamp > '2024-01-15 00:00:00'
LIMIT 100;
```

---

### Graph Databases

**Examples:** Neo4j, Amazon Neptune, ArangoDB

**Strengths:**
- Relationship queries (traversals)
- Pattern matching
- Social networks
- Recommendation engines

**Use Cases:**
```
✓ Social networks (friends, followers)
✓ Fraud detection (transaction patterns)
✓ Recommendation systems (similar users/products)
✓ Knowledge graphs
```

**Example: Social Network (Neo4j)**
```cypher
// Create users and relationships
CREATE (alice:User {name: 'Alice', age: 30})
CREATE (bob:User {name: 'Bob', age: 25})
CREATE (carol:User {name: 'Carol', age: 28})
CREATE (alice)-[:FOLLOWS]->(bob)
CREATE (bob)-[:FOLLOWS]->(carol)
CREATE (carol)-[:FOLLOWS]->(alice)

// Find friends of friends
MATCH (user:User {name: 'Alice'})-[:FOLLOWS]->()-[:FOLLOWS]->(fof)
WHERE fof <> user
RETURN DISTINCT fof.name

// Shortest path between users
MATCH path = shortestPath(
  (alice:User {name: 'Alice'})-[:FOLLOWS*]-(bob:User {name: 'Bob'})
)
RETURN path
```

---

### Time-Series Databases

**Examples:** InfluxDB, TimescaleDB, Prometheus

**Strengths:**
- Optimized for time-stamped data
- Efficient compression
- Downsampling and aggregation
- Built-in retention policies

**Use Cases:**
```
✓ Application metrics
✓ Server monitoring
✓ IoT sensor data
✓ Financial tick data
```

**Example: Application Metrics (InfluxDB)**
```python
from influxdb_client import InfluxDBClient, Point

client = InfluxDBClient(url="http://localhost:8086", token="my-token")
write_api = client.write_api()

# Write metric
point = Point("http_requests") \
    .tag("endpoint", "/api/users") \
    .tag("status", "200") \
    .field("response_time", 45.2) \
    .time(datetime.utcnow())

write_api.write(bucket="my-bucket", record=point)

# Query aggregated metrics
query = '''
from(bucket: "my-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "http_requests")
  |> filter(fn: (r) => r.endpoint == "/api/users")
  |> aggregateWindow(every: 5m, fn: mean)
'''

result = client.query_api().query(query)
```

---

## 2. Data Consistency Patterns

### Two-Phase Commit (2PC)

**Goal:** Atomic commit across multiple databases.

**How it works:**
```
Phase 1 (Prepare):
Coordinator → All Participants: "Prepare to commit"
Participants → Prepare transaction, lock resources
Participants → Coordinator: "Ready" or "Abort"

Phase 2 (Commit):
If all "Ready":
  Coordinator → All: "Commit"
  Participants → Commit transaction
Else:
  Coordinator → All: "Abort"
  Participants → Rollback transaction
```

**Implementation:**
```python
class TwoPhaseCommitCoordinator:
    def __init__(self, participants):
        self.participants = participants
    
    def execute_transaction(self, transaction):
        # Phase 1: Prepare
        for participant in self.participants:
            if not participant.prepare(transaction):
                self.abort_all(transaction)
                return False
        
        # Phase 2: Commit
        for participant in self.participants:
            participant.commit(transaction)
        
        return True
    
    def abort_all(self, transaction):
        for participant in self.participants:
            participant.abort(transaction)

# Usage
coordinator = TwoPhaseCommitCoordinator([
    OrderDatabase(),
    PaymentDatabase(),
    InventoryDatabase()
])

success = coordinator.execute_transaction({
    'order_id': 123,
    'amount': 99.99,
    'items': ['product1', 'product2']
})
```

**Problems:**
- Blocking protocol (participants wait for coordinator)
- Coordinator is single point of failure
- Slow (two round trips)

---

### Saga Pattern (Revisited)

Already covered in Phase 2, but critical for data consistency.

**Compensating Transactions:**
```python
# Order Saga with compensation
class OrderSaga:
    def execute(self, order):
        try:
            # Step 1: Create order
            order_id = order_service.create(order)
            
            try:
                # Step 2: Process payment
                payment_id = payment_service.charge(order.total)
                
                try:
                    # Step 3: Reserve inventory
                    inventory_service.reserve(order.items)
                    
                    return {"success": True, "order_id": order_id}
                    
                except InventoryError:
                    # Compensate: Refund payment
                    payment_service.refund(payment_id)
                    raise
                    
            except PaymentError:
                # Compensate: Cancel order
                order_service.cancel(order_id)
                raise
                
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

### Idempotency

**Definition:** Operation can be applied multiple times without changing result beyond initial application.

**Why needed:** Network retries may cause duplicate requests.

**Implementation:**
```python
class IdempotentPaymentService:
    def __init__(self):
        self.processed = {}  # In production: use database
    
    def charge(self, amount, idempotency_key):
        # Check if already processed
        if idempotency_key in self.processed:
            return self.processed[idempotency_key]
        
        # Process payment
        result = stripe.charge(amount)
        
        # Store result
        self.processed[idempotency_key] = result
        
        return result

# Client usage
payment_service = IdempotentPaymentService()

# Safe to retry
result1 = payment_service.charge(99.99, "order-123-payment")
result2 = payment_service.charge(99.99, "order-123-payment")  # Same result, no double charge

assert result1 == result2
```

---

## 3. Data Replication

### Master-Slave Replication

**Pattern:** One master (accepts writes), multiple replicas (serve reads).

**Implementation:**
```
Master (Primary):
├── Accepts all writes
├── Replicates to slaves
└── Handles conflicts

Slaves (Replicas):
├── Receive updates from master
├── Serve read requests
└── Cannot accept writes
```

**Example: PostgreSQL Replication**
```python
class DatabaseRouter:
    def __init__(self, master, replicas):
        self.master = master
        self.replicas = replicas
    
    def write(self, query, params):
        return self.master.execute(query, params)
    
    def read(self, query, params):
        # Load balance reads across replicas
        replica = random.choice(self.replicas)
        return replica.execute(query, params)

# Usage
db = DatabaseRouter(
    master=PostgreSQL("master.db.internal"),
    replicas=[
        PostgreSQL("replica1.db.internal"),
        PostgreSQL("replica2.db.internal")
    ]
)

# Write goes to master
db.write("INSERT INTO users (name) VALUES (?)", ["Alice"])

# Read from replica
users = db.read("SELECT * FROM users", [])
```

**Trade-offs:**
- ✓ Scales reads horizontally
- ✓ Simple to understand
- ✗ Replication lag (eventual consistency)
- ✗ Writes don't scale
- ✗ Master is single point of failure

---

### Multi-Master Replication

**Pattern:** Multiple nodes accept writes, replicate to each other.

**Challenges:**
- Conflict resolution (two masters update same row)
- Complexity

**Conflict Resolution Strategies:**

**1. Last Write Wins (LWW)**
```python
# Use timestamp to determine winner
def resolve_conflict(version1, version2):
    if version1['timestamp'] > version2['timestamp']:
        return version1
    else:
        return version2
```

**2. Application-Specific**
```python
# Shopping cart: Merge items
def resolve_cart_conflict(cart1, cart2):
    # Union of items
    merged_items = {}
    
    for item_id, qty in cart1['items'].items():
        merged_items[item_id] = qty
    
    for item_id, qty in cart2['items'].items():
        if item_id in merged_items:
            # Take max quantity
            merged_items[item_id] = max(merged_items[item_id], qty)
        else:
            merged_items[item_id] = qty
    
    return {'items': merged_items}
```

---

### Quorum-Based Replication

**Pattern:** Require majority of nodes to agree on read/write.

**Formula:**
```
R + W > N

R = Read quorum
W = Write quorum
N = Total replicas

Example:
N = 5 replicas
W = 3 (write to 3 replicas)
R = 3 (read from 3 replicas)
3 + 3 > 5 ✓ (guarantees overlap)
```

**Configurations:**
```
Strong Consistency:
W = N, R = 1 (write to all, read from any)

Eventual Consistency:
W = 1, R = N (write to any, read from all)

Balanced:
W = (N/2)+1, R = (N/2)+1 (quorum for both)
```

**Example: Cassandra**
```python
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel

cluster = Cluster(['localhost'])
session = cluster.connect('my_keyspace')

# Write with quorum
query = SimpleStatement(
    "INSERT INTO users (id, name) VALUES (?, ?)",
    consistency_level=ConsistencyLevel.QUORUM
)
session.execute(query, (123, 'Alice'))

# Read with quorum
query = SimpleStatement(
    "SELECT * FROM users WHERE id = ?",
    consistency_level=ConsistencyLevel.QUORUM
)
result = session.execute(query, (123,))
```

---

## Summary

### Choosing the Right Database

```
Relational (PostgreSQL):
✓ ACID transactions
✓ Complex queries
✓ Strict schema
Use for: Orders, payments, user auth

Document (MongoDB):
✓ Flexible schema
✓ Nested data
✓ Fast reads
Use for: Product catalogs, CMS

Key-Value (Redis):
✓ Extreme speed
✓ Simple model
✓ Caching
Use for: Sessions, rate limiting

Column-Family (Cassandra):
✓ Massive scale
✓ Time-series
✓ High writes
Use for: Logs, analytics, IoT

Graph (Neo4j):
✓ Relationships
✓ Traversals
Use for: Social networks, recommendations

Time-Series (InfluxDB):
✓ Metrics
✓ Monitoring
Use for: Application performance monitoring
```

### Consistency Patterns

```
Two-Phase Commit:
✓ Strong consistency
✗ Slow, blocking
Use: Critical transactions within single datacenter

Saga:
✓ Eventual consistency
✓ Long-running processes
Use: Cross-service workflows

Idempotency:
✓ Safe retries
Use: All distributed operations
```

### Replication

```
Master-Slave:
✓ Simple
✓ Scales reads
Use: Read-heavy workloads

Multi-Master:
✓ Scales writes
✗ Complex conflicts
Use: Global distribution

Quorum:
✓ Tunable consistency
✓ Fault tolerant
Use: When need both consistency and availability
```

---

## Further Reading

**Books:**
- "Designing Data-Intensive Applications" by Martin Kleppmann (Ch 5-9)
- "Database Internals" by Alex Petrov
- "Seven Databases in Seven Weeks" by Eric Redmond

**Documentation:**
- PostgreSQL replication
- MongoDB sharding
- Cassandra architecture
- Neo4j graph algorithms

**Next Topics:**
- Phase 5: Reliability & Resilience
- Phase 6: Observability & Monitoring

---

**Remember:** Polyglot persistence is powerful but adds operational complexity. Start with one database, add others only when clear need exists.
