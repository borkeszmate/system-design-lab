# Scalability & Performance

## Overview

Scalability is the ability of a system to handle increased load by adding resources. Performance is how efficiently a system uses those resources. This document covers essential techniques for building systems that scale horizontally and vertically while maintaining good performance.

**Key Topics:**
1. **Caching Strategies** - Speed up reads, reduce database load
2. **Load Balancing** - Distribute traffic across multiple servers
3. **Database Scaling** - Handle growing data and traffic
4. **Asynchronous Processing** - Decouple heavy operations

These patterns work together to create systems that can handle millions of users and petabytes of data.

---

## 1. Caching Strategies

### What is Caching?

**Definition:** Temporarily storing frequently accessed data in a fast-access location to reduce latency and load on the origin.

**Fundamental Principle:** 80/20 rule - 20% of data accounts for 80% of requests.

### Cache Hierarchy

```
Fastest/Smallest → Slowest/Largest

L1 Cache (CPU, nanoseconds)
    ↓
L2/L3 Cache (CPU, nanoseconds)
    ↓
Application Memory (RAM, microseconds)
    ↓
Local Cache (Redis/Memcached, milliseconds)
    ↓
Database (SSD/HDD, milliseconds-seconds)
    ↓
Remote Storage (S3, seconds)
```

### Cache Patterns

#### 1. Cache-Aside (Lazy Loading)

**Pattern:** Application checks cache first; on miss, loads from DB and populates cache.

**Flow:**
```
1. Request data
2. Check cache
   ├─ Hit: Return cached data
   └─ Miss:
       ├─ Load from database
       ├─ Write to cache
       └─ Return data
```

**Implementation:**
```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379)

def get_user(user_id):
    # Try cache first
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)

    if cached:
        print("Cache hit!")
        return json.loads(cached)

    # Cache miss - load from database
    print("Cache miss - loading from DB")
    user = database.query("SELECT * FROM users WHERE id = ?", user_id)

    if user:
        # Populate cache (TTL: 1 hour)
        cache.setex(cache_key, 3600, json.dumps(user))

    return user

# Usage
user = get_user(123)  # First call: DB + cache write
user = get_user(123)  # Second call: Cache hit (fast!)
```

**Pros:**
- Simple to implement
- Only caches requested data
- Cache failures don't prevent application from working

**Cons:**
- Initial request is slow (cache miss)
- Potential for stale data
- Cache stampede risk (many requests miss simultaneously)

**Best for:** Read-heavy workloads, data that doesn't change frequently

---

#### 2. Write-Through Cache

**Pattern:** Application writes to cache and database simultaneously; cache always consistent.

**Flow:**
```
Write Request:
1. Write to cache
2. Write to database (synchronous)
3. Return success

Read Request:
1. Check cache (always has data)
2. Return from cache
```

**Implementation:**
```python
def update_user(user_id, data):
    cache_key = f"user:{user_id}"

    # Write to cache first
    cache.setex(cache_key, 3600, json.dumps(data))

    # Then write to database
    database.execute(
        "UPDATE users SET name = ?, email = ? WHERE id = ?",
        data['name'], data['email'], user_id
    )

    return data

def get_user(user_id):
    # Cache always has data (if it exists)
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)

    if cached:
        return json.loads(cached)

    # Not in cache or DB
    return None
```

**Pros:**
- Cache always consistent with DB
- Read misses are rare
- Good for read-heavy, frequently updated data

**Cons:**
- Every write is slower (two operations)
- Unused data still cached
- Cache failure stops writes

**Best for:** Data that's frequently read and updated

---

#### 3. Write-Behind (Write-Back) Cache

**Pattern:** Write to cache immediately; asynchronously flush to database later.

**Flow:**
```
Write Request:
1. Write to cache (fast)
2. Return success immediately
3. Background: Flush to database

Read Request:
1. Always read from cache
```

**Implementation:**
```python
import threading
import queue
import time

# Queue for async DB writes
write_queue = queue.Queue()

def async_db_writer():
    """Background thread that flushes cache to DB"""
    while True:
        try:
            # Get next write operation
            operation = write_queue.get(timeout=1)

            # Write to database
            database.execute(operation['query'], *operation['params'])

            write_queue.task_done()
        except queue.Empty:
            continue

# Start background writer
writer_thread = threading.Thread(target=async_db_writer, daemon=True)
writer_thread.start()

def update_user(user_id, data):
    cache_key = f"user:{user_id}"

    # Write to cache (fast)
    cache.setex(cache_key, 3600, json.dumps(data))

    # Queue DB write (async)
    write_queue.put({
        'query': "UPDATE users SET name = ?, email = ? WHERE id = ?",
        'params': [data['name'], data['email'], user_id]
    })

    # Return immediately (before DB write completes)
    return data

def get_user(user_id):
    # Always read from cache
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)
    return json.loads(cached) if cached else None
```

**Pros:**
- Very fast writes
- Reduced database load
- Can batch multiple writes

**Cons:**
- Risk of data loss if cache fails before flush
- Complex error handling
- Eventual consistency between cache and DB

**Best for:** Write-heavy workloads, gaming leaderboards, counters

---

### Content Delivery Networks (CDN)

**What is CDN:** Geographically distributed cache servers that serve static content close to users.

**How it works:**
```
User in Tokyo → CDN Edge Server (Tokyo) → Origin Server (US)
                      ↓ (cache)
                 Subsequent requests served from Tokyo

Latency: 150ms → 5ms (30x faster!)
```

**CDN Flow:**
```
1. User requests https://cdn.example.com/image.jpg
2. DNS resolves to nearest edge server
3. Edge server checks cache:
   ├─ Hit: Serve from cache (fast)
   └─ Miss:
       ├─ Fetch from origin
       ├─ Cache at edge
       └─ Serve to user
```

**Implementation with CloudFront:**
```python
# S3 + CloudFront setup
import boto3

s3 = boto3.client('s3')
cloudfront = boto3.client('cloudfront')

# Upload to S3
s3.upload_file(
    '/path/to/image.jpg',
    'my-bucket',
    'images/product-123.jpg',
    ExtraArgs={
        'ContentType': 'image/jpeg',
        'CacheControl': 'max-age=86400'  # Cache for 1 day
    }
)

# CloudFront automatically distributes to edge locations
# URL: https://d123456.cloudfront.net/images/product-123.jpg

# Invalidate cache when image changes
cloudfront.create_invalidation(
    DistributionId='E123456',
    InvalidationBatch={
        'Paths': {
            'Quantity': 1,
            'Items': ['/images/product-123.jpg']
        },
        'CallerReference': str(time.time())
    }
)
```

**CDN Benefits:**
- Reduced latency (geographic proximity)
- Reduced origin load
- DDoS protection
- Automatic scaling

**CDN Best Practices:**
```
✓ Cache static assets (images, CSS, JS)
✓ Set appropriate TTLs
✓ Use versioned URLs (style.v2.css)
✓ Enable compression (gzip, brotli)
✗ Don't cache personalized content
✗ Don't cache frequently changing data
```

---

### Redis Caching Patterns

**Redis:** In-memory data store, often used as cache.

#### Pattern: Session Store

```python
import redis
import json
from datetime import timedelta

cache = redis.Redis(host='localhost', port=6379)

def create_session(user_id):
    session_id = generate_uuid()
    session_data = {
        'user_id': user_id,
        'created_at': time.time(),
        'ip': request.remote_addr
    }

    # Store session (TTL: 24 hours)
    cache.setex(
        f"session:{session_id}",
        timedelta(hours=24),
        json.dumps(session_data)
    )

    return session_id

def get_session(session_id):
    session = cache.get(f"session:{session_id}")
    return json.loads(session) if session else None

def extend_session(session_id):
    # Extend TTL by another 24 hours
    cache.expire(f"session:{session_id}", timedelta(hours=24))
```

#### Pattern: Rate Limiting

```python
def is_rate_limited(user_id, max_requests=100, window_seconds=3600):
    key = f"ratelimit:{user_id}"

    # Increment counter
    current = cache.incr(key)

    # Set expiry on first request
    if current == 1:
        cache.expire(key, window_seconds)

    # Check if limit exceeded
    return current > max_requests

# Usage
if is_rate_limited(user_id):
    return {"error": "Rate limit exceeded"}, 429
```

#### Pattern: Leaderboard

```python
# Sorted Sets for rankings
def update_score(user_id, score):
    cache.zadd('leaderboard', {user_id: score})

def get_top_players(count=10):
    # Get top N players (descending score)
    return cache.zrevrange('leaderboard', 0, count-1, withscores=True)

def get_user_rank(user_id):
    # Get rank (0-indexed)
    rank = cache.zrevrank('leaderboard', user_id)
    return rank + 1 if rank is not None else None

# Usage
update_score('alice', 1500)
update_score('bob', 1200)
update_score('charlie', 1800)

top_10 = get_top_players(10)
# [('charlie', 1800), ('alice', 1500), ('bob', 1200)]

alice_rank = get_user_rank('alice')  # 2
```

---

### Cache Invalidation Strategies

**Phil Karlton:** "There are only two hard things in Computer Science: cache invalidation and naming things."

#### 1. Time-To-Live (TTL)

**Approach:** Cache expires after fixed time.

```python
# Cache for 1 hour
cache.setex('user:123', 3600, json.dumps(user_data))

# Different TTLs for different data
cache.setex('product:456', 86400, json.dumps(product))  # 24 hours
cache.setex('trending', 300, json.dumps(trends))  # 5 minutes
```

**Pros:** Simple, predictable
**Cons:** May serve stale data, may refresh too often

**Choose TTL based on:**
- How frequently data changes
- How stale is acceptable
- Load on origin

```
User Profile: 1 hour (changes infrequently)
Product Prices: 5 minutes (changes occasionally)
Stock Levels: 30 seconds (changes frequently)
Trending Topics: 1 minute (real-time feel)
```

#### 2. Explicit Invalidation

**Approach:** Manually delete cache when data changes.

```python
def update_product(product_id, new_data):
    # Update database
    database.execute(
        "UPDATE products SET price = ? WHERE id = ?",
        new_data['price'], product_id
    )

    # Invalidate cache
    cache.delete(f"product:{product_id}")

    # Also invalidate related caches
    cache.delete(f"category:{new_data['category_id']}:products")
    cache.delete('homepage:featured_products')
```

**Pros:** Always fresh, efficient
**Cons:** Easy to forget, complex dependencies

#### 3. Write-Through (Always Consistent)

Already covered - cache updated on every write.

#### 4. Event-Driven Invalidation

**Approach:** Invalidate cache based on events.

```python
# Publish event when data changes
event_bus.publish('product.updated', {
    'product_id': 123,
    'category_id': 5
})

# Cache invalidation subscriber
def on_product_updated(event):
    cache.delete(f"product:{event['product_id']}")
    cache.delete(f"category:{event['category_id']}:products")

event_bus.subscribe('product.updated', on_product_updated)
```

**Pros:** Decoupled, scalable
**Cons:** Eventual consistency, complex

---

### Cache Stampede (Thundering Herd)

**Problem:** Many requests simultaneously discover cache miss, all query database.

```
Cache expires at 10:00:00
10:00:01 - 1000 requests arrive
All see cache miss
All query database simultaneously
Database overwhelmed!
```

**Solution 1: Lock-Based (Request Coalescing)**

```python
import threading

# Lock per cache key
cache_locks = {}
lock_manager = threading.Lock()

def get_user_safe(user_id):
    cache_key = f"user:{user_id}"

    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Get/create lock for this key
    with lock_manager:
        if cache_key not in cache_locks:
            cache_locks[cache_key] = threading.Lock()
        key_lock = cache_locks[cache_key]

    # Only one request loads from DB
    with key_lock:
        # Double-check cache (may have been populated while waiting)
        cached = cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Load from database
        user = database.query("SELECT * FROM users WHERE id = ?", user_id)

        if user:
            cache.setex(cache_key, 3600, json.dumps(user))

        return user
```

**Solution 2: Probabilistic Early Expiration**

```python
import random
import time

def get_with_probabilistic_refresh(key, ttl, fetch_func):
    cached = cache.get(key)

    if cached:
        data = json.loads(cached)

        # Check if should refresh early
        time_left = cache.ttl(key)
        if time_left > 0:
            # Probability of refresh increases as expiry approaches
            refresh_probability = 1 - (time_left / ttl)

            if random.random() < refresh_probability:
                # Refresh in background
                threading.Thread(
                    target=lambda: cache.setex(key, ttl, json.dumps(fetch_func()))
                ).start()

        return data

    # Cache miss - load and cache
    data = fetch_func()
    cache.setex(key, ttl, json.dumps(data))
    return data
```

---

### Caching Best Practices

```
✓ Cache near the requester
  - Browser cache (HTTP headers)
  - CDN (static assets)
  - Application cache (API responses)
  - Database cache (query results)

✓ Cache frequently accessed, rarely changing data
  - Product catalogs
  - User profiles
  - Configuration

✗ Don't cache
  - User-specific sensitive data (unless encrypted)
  - Real-time data (stock prices)
  - Data with strict consistency requirements

✓ Set appropriate TTLs
  - Static assets: Days (versioned URLs)
  - Semi-static: Hours (product descriptions)
  - Dynamic: Minutes (prices, inventory)

✓ Monitor cache hit rates
  - Target: 80%+ hit rate
  - Low hit rate = wrong data cached or TTL too short

✓ Have invalidation strategy
  - TTL + explicit invalidation
  - Event-driven
  - Cache versioning

✓ Handle cache failures gracefully
  - Cache miss = load from DB (don't fail request)
  - Cache service down = bypass cache
```

---

## 2. Load Balancing

### What is Load Balancing?

**Definition:** Distributing incoming requests across multiple servers to improve responsiveness, availability, and prevent overload.

**Why needed:**
```
Single Server:
├── 1000 requests/sec = Overwhelmed
└── Server fails = Complete outage

Load Balanced (3 servers):
├── 1000 requests/sec ÷ 3 = 333 req/sec each (manageable)
└── 1 server fails = Other 2 handle load (partial degradation)
```

### Load Balancer Types

#### Layer 4 (Transport Layer) Load Balancing

**What:** Routes based on IP and port (TCP/UDP).

**Characteristics:**
- Fast (no payload inspection)
- Protocol-agnostic
- Connection-level routing
- Cannot make decisions based on content

**How it works:**
```
Client → Load Balancer (L4) → Backend Server

LB sees:
├── Source IP: 203.0.113.5
├── Destination Port: 443
└── Protocol: TCP

LB does NOT see:
├── HTTP headers
├── URL path
└── Request content
```

**Use cases:**
- High throughput needed
- Non-HTTP protocols
- Simple distribution

#### Layer 7 (Application Layer) Load Balancing

**What:** Routes based on application data (HTTP headers, URLs, cookies).

**Characteristics:**
- Content-aware routing
- Can modify requests/responses
- SSL termination
- Slower than L4 (payload inspection)

**How it works:**
```
Client → Load Balancer (L7) → Backend Server

LB sees:
├── HTTP method: GET
├── URL: /api/users/123
├── Headers: User-Agent, Cookie
└── Request body

LB can route based on:
├── Path: /api/* → API servers
├── Header: X-Version: v2 → New servers
└── Cookie: session=... → Sticky session
```

**Use cases:**
- Content-based routing
- A/B testing
- Microservices routing

**Example: NGINX L7 Config**
```nginx
http {
    upstream api_servers {
        server api1.example.com;
        server api2.example.com;
        server api3.example.com;
    }

    upstream web_servers {
        server web1.example.com;
        server web2.example.com;
    }

    server {
        listen 80;

        # Route API requests
        location /api/ {
            proxy_pass http://api_servers;
        }

        # Route web requests
        location / {
            proxy_pass http://web_servers;
        }

        # Route to specific server for beta users
        location /beta/ {
            if ($cookie_user_type = "beta") {
                proxy_pass http://beta_server;
            }
        }
    }
}
```

---

### Load Balancing Algorithms

#### 1. Round Robin

**How:** Distribute requests sequentially across servers.

```
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A (cycle repeats)
```

**Implementation:**
```python
class RoundRobinLoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.current = 0

    def get_server(self):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

# Usage
lb = RoundRobinLoadBalancer(['server1', 'server2', 'server3'])
print(lb.get_server())  # server1
print(lb.get_server())  # server2
print(lb.get_server())  # server3
print(lb.get_server())  # server1
```

**Pros:** Simple, fair distribution
**Cons:** Doesn't consider server load or capacity

**Best for:** Homogeneous servers with similar capacity

#### 2. Weighted Round Robin

**How:** Servers with higher weight receive more requests.

```
Servers:
├── A (weight: 3)
├── B (weight: 2)
└── C (weight: 1)

Distribution:
A, A, A, B, B, C, (repeat)
```

**Implementation:**
```python
class WeightedRoundRobinLoadBalancer:
    def __init__(self, servers):
        # servers = [{'name': 'A', 'weight': 3}, ...]
        self.servers = []
        for server in servers:
            # Add server 'weight' times
            self.servers.extend([server['name']] * server['weight'])
        self.current = 0

    def get_server(self):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

# Usage
lb = WeightedRoundRobinLoadBalancer([
    {'name': 'server1', 'weight': 3},  # Powerful server
    {'name': 'server2', 'weight': 2},  # Medium server
    {'name': 'server3', 'weight': 1}   # Weak server
])
```

**Best for:** Heterogeneous servers with different capacities

#### 3. Least Connections

**How:** Route to server with fewest active connections.

```
Server A: 10 connections
Server B: 5 connections
Server C: 8 connections

New request → Server B (least connections)
```

**Implementation:**
```python
class LeastConnectionsLoadBalancer:
    def __init__(self, servers):
        self.connections = {server: 0 for server in servers}

    def get_server(self):
        # Find server with minimum connections
        return min(self.connections, key=self.connections.get)

    def on_connection_start(self, server):
        self.connections[server] += 1

    def on_connection_end(self, server):
        self.connections[server] -= 1

# Usage
lb = LeastConnectionsLoadBalancer(['server1', 'server2', 'server3'])

# Request arrives
server = lb.get_server()  # server1 (0 connections)
lb.on_connection_start(server)

# Another request
server = lb.get_server()  # server2 (0 connections)
lb.on_connection_start(server)

# First request completes
lb.on_connection_end('server1')  # server1 back to 0
```

**Best for:** Long-lived connections, variable request processing time

#### 4. IP Hash (Consistent Hashing)

**How:** Hash client IP to determine server (same client always goes to same server).

```
hash(client_ip) % num_servers = server_index

Client 203.0.113.5 → hash → Server A (always)
Client 203.0.113.6 → hash → Server C (always)
```

**Implementation:**
```python
import hashlib

class IPHashLoadBalancer:
    def __init__(self, servers):
        self.servers = servers

    def get_server(self, client_ip):
        # Hash IP to get consistent server
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        server_index = hash_value % len(self.servers)
        return self.servers[server_index]

# Usage
lb = IPHashLoadBalancer(['server1', 'server2', 'server3'])

# Same IP always goes to same server
print(lb.get_server('203.0.113.5'))  # server2
print(lb.get_server('203.0.113.5'))  # server2 (consistent!)
print(lb.get_server('203.0.113.6'))  # server1
```

**Pros:** Session affinity without storing state
**Cons:** Uneven distribution, adding/removing servers disrupts mapping

**Best for:** Stateful applications, caching

---

### Health Checks

**Why:** Don't route to unhealthy servers.

#### Active Health Checks

**Approach:** Load balancer periodically probes servers.

```python
import requests
import time
import threading

class HealthCheckLoadBalancer:
    def __init__(self, servers, check_interval=30):
        self.servers = servers
        self.healthy_servers = set(servers)
        self.check_interval = check_interval

        # Start health check thread
        threading.Thread(target=self._health_check_loop, daemon=True).start()

    def _health_check_loop(self):
        while True:
            for server in self.servers:
                if self._is_healthy(server):
                    self.healthy_servers.add(server)
                else:
                    self.healthy_servers.discard(server)
                    print(f"Server {server} is unhealthy!")

            time.sleep(self.check_interval)

    def _is_healthy(self, server):
        try:
            response = requests.get(f'http://{server}/health', timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_server(self):
        if not self.healthy_servers:
            raise Exception("No healthy servers available")

        # Round robin among healthy servers
        return list(self.healthy_servers)[0]
```

**Health Check Endpoint:**
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    # Check database connection
    try:
        database.execute("SELECT 1")
    except:
        return jsonify({"status": "unhealthy"}), 503

    # Check dependencies
    if not redis.ping():
        return jsonify({"status": "unhealthy"}), 503

    return jsonify({"status": "healthy"}), 200
```

#### Passive Health Checks

**Approach:** Monitor actual request failures.

```python
class PassiveHealthCheckLoadBalancer:
    def __init__(self, servers, failure_threshold=3):
        self.servers = servers
        self.failures = {server: 0 for server in servers}
        self.threshold = failure_threshold
        self.healthy_servers = set(servers)

    def on_request_success(self, server):
        # Reset failure count
        self.failures[server] = 0
        self.healthy_servers.add(server)

    def on_request_failure(self, server):
        # Increment failure count
        self.failures[server] += 1

        # Mark unhealthy if threshold exceeded
        if self.failures[server] >= self.threshold:
            self.healthy_servers.discard(server)
            print(f"Server {server} marked unhealthy after {self.failures[server]} failures")

    def get_server(self):
        if not self.healthy_servers:
            # Fallback: try any server
            return self.servers[0]

        return list(self.healthy_servers)[0]
```

---

### Circuit Breaker Pattern (with Load Balancer)

**Combine load balancing with circuit breaker:**

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, don't send requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreakerLoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.circuits = {
            server: {
                'state': CircuitState.CLOSED,
                'failures': 0,
                'last_failure_time': None
            }
            for server in servers
        }
        self.failure_threshold = 5
        self.timeout = 60  # seconds

    def get_server(self):
        for server in self.servers:
            circuit = self.circuits[server]

            if circuit['state'] == CircuitState.CLOSED:
                return server

            elif circuit['state'] == CircuitState.OPEN:
                # Check if timeout elapsed
                if time.time() - circuit['last_failure_time'] > self.timeout:
                    circuit['state'] = CircuitState.HALF_OPEN
                    return server

            elif circuit['state'] == CircuitState.HALF_OPEN:
                # Give it a try
                return server

        raise Exception("All circuits open!")

    def on_success(self, server):
        circuit = self.circuits[server]
        circuit['failures'] = 0
        circuit['state'] = CircuitState.CLOSED

    def on_failure(self, server):
        circuit = self.circuits[server]
        circuit['failures'] += 1
        circuit['last_failure_time'] = time.time()

        if circuit['failures'] >= self.failure_threshold:
            circuit['state'] = CircuitState.OPEN
            print(f"Circuit breaker OPEN for {server}")
```

---

### Global Load Balancing

**Scenario:** Users worldwide, datacenters in multiple regions.

**Strategy:**

```
DNS-Based Global Load Balancing:

User in Japan → DNS query → asia.example.com → Tokyo datacenter
User in USA → DNS query → usa.example.com → Virginia datacenter
User in EU → DNS query → eu.example.com → Frankfurt datacenter
```

**Implementation: Route 53 (AWS)**
```python
import boto3

route53 = boto3.client('route53')

# Create latency-based routing
route53.change_resource_record_sets(
    HostedZoneId='Z123456',
    ChangeBatch={
        'Changes': [
            {
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': 'api.example.com',
                    'Type': 'A',
                    'SetIdentifier': 'US-East',
                    'Region': 'us-east-1',
                    'TTL': 60,
                    'ResourceRecords': [{'Value': '54.1.2.3'}]
                }
            },
            {
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': 'api.example.com',
                    'Type': 'A',
                    'SetIdentifier': 'EU-West',
                    'Region': 'eu-west-1',
                    'TTL': 60,
                    'ResourceRecords': [{'Value': '52.4.5.6'}]
                }
            },
            {
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': 'api.example.com',
                    'Type': 'A',
                    'SetIdentifier': 'AP-Northeast',
                    'Region': 'ap-northeast-1',
                    'TTL': 60,
                    'ResourceRecords': [{'Value': '13.7.8.9'}]
                }
            }
        ]
    }
)

# Route 53 automatically routes to lowest latency endpoint
```

---

## 3. Database Scaling

### Vertical vs Horizontal Scaling

**Vertical Scaling (Scale Up):**
```
Before: 4 CPU, 8 GB RAM
After:  16 CPU, 64 GB RAM

Pros:
✓ Simple (no code changes)
✓ No sharding complexity

Cons:
✗ Hardware limits
✗ Expensive (exponential cost)
✗ Single point of failure
```

**Horizontal Scaling (Scale Out):**
```
Before: 1 server (4 CPU, 8 GB)
After:  4 servers (4 CPU, 8 GB each)

Pros:
✓ No theoretical limit
✓ Linear cost growth
✓ Fault tolerance

Cons:
✗ Complex (sharding, replication)
✗ Eventual consistency
```

---

### Read Replicas

**Pattern:** Separate read and write databases.

**Architecture:**
```
        Write Requests
             ↓
    [Master Database] (Primary)
             ↓ (replicate)
    ┌────────┼────────┐
    ↓        ↓        ↓
[Replica 1] [Replica 2] [Replica 3]
    ↑        ↑        ↑
Read Requests (load balanced)

Write: Go to master
Read: Load balanced across replicas
```

**Benefits:**
- Scale reads horizontally
- Offload analytics queries
- Geographic distribution

**Trade-offs:**
- Replication lag (eventual consistency)
- Writes don't scale
- More complex

**Implementation:**
```python
import random

class DatabaseRouter:
    def __init__(self, master, replicas):
        self.master = master
        self.replicas = replicas

    def execute_write(self, query, params):
        # All writes go to master
        return self.master.execute(query, params)

    def execute_read(self, query, params):
        # Reads load balanced across replicas
        replica = random.choice(self.replicas)
        return replica.execute(query, params)

# Usage
db = DatabaseRouter(
    master=PostgreSQL('master.db.com'),
    replicas=[
        PostgreSQL('replica1.db.com'),
        PostgreSQL('replica2.db.com'),
        PostgreSQL('replica3.db.com')
    ]
)

# Write
db.execute_write("INSERT INTO users (name) VALUES (?)", ['Alice'])

# Read
users = db.execute_read("SELECT * FROM users", [])
```

**Handling Replication Lag:**
```python
def create_user(name):
    # Write to master
    user_id = db.execute_write(
        "INSERT INTO users (name) VALUES (?) RETURNING id",
        [name]
    )[0]['id']

    # Read from master (not replica) to avoid lag
    user = db.master.execute(
        "SELECT * FROM users WHERE id = ?",
        [user_id]
    )[0]

    return user

# Or: Read from replica with retry
def get_user_with_retry(user_id, max_attempts=3):
    for attempt in range(max_attempts):
        user = db.execute_read("SELECT * FROM users WHERE id = ?", [user_id])
        if user:
            return user
        time.sleep(0.1 * (attempt + 1))  # Wait for replication

    # Fallback to master
    return db.master.execute("SELECT * FROM users WHERE id = ?", [user_id])[0]
```

---

### Database Sharding

**Definition:** Partition data across multiple databases.

**Why:** When single database can't handle load or data size.

#### Horizontal Sharding (Partition by Row)

**Strategy:** Split table rows across multiple databases.

**Example: User Sharding by ID**
```
Users Table (100M users):

Shard 0: user_id % 4 == 0 (25M users)
Shard 1: user_id % 4 == 1 (25M users)
Shard 2: user_id % 4 == 2 (25M users)
Shard 3: user_id % 4 == 3 (25M users)
```

**Implementation:**
```python
class ShardedDatabase:
    def __init__(self, shards):
        self.shards = shards  # List of database connections

    def get_shard(self, user_id):
        shard_index = user_id % len(self.shards)
        return self.shards[shard_index]

    def get_user(self, user_id):
        shard = self.get_shard(user_id)
        return shard.query("SELECT * FROM users WHERE id = ?", [user_id])[0]

    def create_user(self, name):
        # Determine shard for new user
        user_id = generate_unique_id()
        shard = self.get_shard(user_id)

        shard.execute(
            "INSERT INTO users (id, name) VALUES (?, ?)",
            [user_id, name]
        )
        return user_id

# Usage
db = ShardedDatabase([
    PostgreSQL('shard0.db.com'),
    PostgreSQL('shard1.db.com'),
    PostgreSQL('shard2.db.com'),
    PostgreSQL('shard3.db.com')
])

user = db.get_user(123)  # Routes to shard 3 (123 % 4)
```

**Sharding Strategies:**

1. **Hash-Based Sharding**
   ```python
   shard = hash(user_id) % num_shards
   ```
   - Pros: Even distribution
   - Cons: Hard to add shards

2. **Range-Based Sharding**
   ```python
   if user_id < 1000000:
       shard = 0
   elif user_id < 2000000:
       shard = 1
   ...
   ```
   - Pros: Easy to add shards
   - Cons: Uneven distribution (hotspots)

3. **Geographic Sharding**
   ```python
   if user.country == 'US':
       shard = us_shard
   elif user.country == 'EU':
       shard = eu_shard
   ```
   - Pros: Locality, regulatory compliance
   - Cons: Uneven distribution

**Challenges:**

```
✗ Cross-shard queries (joins are expensive)
✗ Resharding (adding/removing shards)
✗ Hotspots (uneven data distribution)
✗ Complexity (application must be shard-aware)
```

**Cross-Shard Query Example:**
```python
def get_all_users_by_country(country):
    # Must query ALL shards
    results = []
    for shard in db.shards:
        shard_results = shard.query(
            "SELECT * FROM users WHERE country = ?",
            [country]
        )
        results.extend(shard_results)

    return results

# Slow! Queries all shards
```

---

### Connection Pooling

**Problem:** Creating database connections is expensive.

**Solution:** Reuse connections from a pool.

**Without Pooling:**
```python
def get_user(user_id):
    conn = create_connection()  # Expensive! (100ms)
    result = conn.query("SELECT * FROM users WHERE id = ?", [user_id])
    conn.close()
    return result

# Each request: 100ms connection + 5ms query = 105ms
```

**With Pooling:**
```python
import psycopg2.pool

# Create pool once at startup
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=5,
    maxconn=20,
    host='db.example.com',
    database='mydb'
)

def get_user(user_id):
    conn = connection_pool.getconn()  # Fast! (reuse existing)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        return result
    finally:
        connection_pool.putconn(conn)  # Return to pool

# Each request: 0ms connection + 5ms query = 5ms
```

**Pool Configuration:**
```python
# Size pool based on concurrent requests
# Rule of thumb: connections = (core_count * 2) + effective_spindle_count

# 4-core server: 10-20 connections typical
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=10,   # Keep 10 connections ready
    maxconn=50,   # Max 50 concurrent connections
    host='db.example.com',
    database='mydb',
    connect_timeout=5
)
```

---

## Summary

### Key Takeaways

**Caching:**
- Cache-aside: Simple, lazy loading
- Write-through: Always consistent
- Write-behind: Fast writes, eventual consistency
- CDN: Cache static assets near users
- Redis: Session store, rate limiting, leaderboards
- Invalidation: TTL, explicit, event-driven
- Avoid cache stampede with locks or probabilistic refresh

**Load Balancing:**
- L4: Fast, protocol-agnostic
- L7: Content-aware, flexible routing
- Algorithms: Round robin, least connections, IP hash
- Health checks: Active and passive
- Circuit breakers: Prevent cascading failures
- Global LB: Route users to nearest datacenter

**Database Scaling:**
- Read replicas: Scale reads, replication lag
- Sharding: Scale writes, complex
- Connection pooling: Reuse connections
- Denormalization: Trade writes for fast reads

**Asynchronous Processing:**
- Message queues: Decouple operations
- Job queues: Background processing
- Backpressure: Handle overload
- Dead letter queues: Handle failures

---

## Further Reading

**Books:**
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "High Performance Browser Networking" by Ilya Grigorik
- "Database Internals" by Alex Petrov

**Online Resources:**
- Redis documentation
- NGINX load balancing guide
- AWS Well-Architected Framework

**Next Topics:**
- Phase 4: Data Management (consistency, replication)
- Phase 5: Reliability & Resilience
- Phase 6: Observability & Monitoring

---

**Remember:** Scalability isn't about handling infinite load, it's about graceful degradation and knowing your limits. Measure, optimize bottlenecks, repeat.
