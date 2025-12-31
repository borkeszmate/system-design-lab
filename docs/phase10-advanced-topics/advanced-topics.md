# Phase 10: Advanced Topics

## Overview

Cutting-edge technologies and optimization techniques for modern distributed systems. This phase explores serverless architectures, edge computing, modern API patterns, service mesh, and advanced performance optimization.

**Key Focus:** Understanding emerging patterns and when to apply them.

---

## Table of Contents

1. [Serverless Architecture](#1-serverless-architecture)
2. [Edge Computing](#2-edge-computing)
3. [Modern API Patterns](#3-modern-api-patterns)
4. [Service Mesh](#4-service-mesh)
5. [Performance Optimization](#5-performance-optimization)
6. [Emerging Technologies](#6-emerging-technologies)

---

## 1. Serverless Architecture

### 1.1 What is Serverless?

**Definition:** Run code without managing servers. Pay only for execution time.

**Benefits:**
- No server management
- Automatic scaling (0 to ∞)
- Pay-per-use pricing
- Built-in high availability

**Drawbacks:**
- Cold start latency
- Vendor lock-in
- Stateless (requires external state)
- Limited execution time (< 15 minutes)

### 1.2 AWS Lambda Example

```python
# handler.py
import json
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Triggered when image uploaded to S3.
    Generate thumbnail and save metadata.
    """
    # Extract S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Download image
    image_data = s3.get_object(Bucket=bucket, Key=key)['Body'].read()

    # Generate thumbnail
    thumbnail = generate_thumbnail(image_data, size=(200, 200))

    # Upload thumbnail
    thumbnail_key = f"thumbnails/{key}"
    s3.put_object(
        Bucket=bucket,
        Key=thumbnail_key,
        Body=thumbnail,
        ContentType='image/jpeg'
    )

    # Save metadata to DynamoDB
    table = dynamodb.Table('images')
    table.put_item(Item={
        'image_id': key,
        'thumbnail_url': f"s3://{bucket}/{thumbnail_key}",
        'size': len(image_data),
        'created_at': context.aws_request_id
    })

    return {
        'statusCode': 200,
        'body': json.dumps({'thumbnail': thumbnail_key})
    }
```

**Deployment (Serverless Framework):**

```yaml
# serverless.yml
service: image-processor

provider:
  name: aws
  runtime: python3.11
  region: us-east-1

functions:
  processImage:
    handler: handler.lambda_handler
    events:
      - s3:
          bucket: my-images-bucket
          event: s3:ObjectCreated:*
          rules:
            - prefix: uploads/
            - suffix: .jpg
    timeout: 60  # seconds
    memorySize: 1024  # MB
    environment:
      THUMBNAIL_SIZE: "200x200"

resources:
  Resources:
    ImagesDynamoDBTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: images
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: image_id
            AttributeType: S
        KeySchema:
          - AttributeName: image_id
            KeyType: HASH
```

### 1.3 Cold Start Mitigation

```python
# Keep function warm with scheduled pings
def keep_warm_handler(event, context):
    """Ping function every 5 minutes to keep it warm"""
    return {'statusCode': 200}

# serverless.yml
functions:
  keepWarm:
    handler: handler.keep_warm_handler
    events:
      - schedule: rate(5 minutes)

# OR: Use provisioned concurrency (costs more)
# serverless.yml
functions:
  api:
    provisionedConcurrency: 3  # Keep 3 instances warm
```

### 1.4 When to Use Serverless

**✅ Good fit:**
- Event-driven workloads (S3 uploads, SQS messages)
- Scheduled tasks (cron jobs)
- Webhooks and API backends (low traffic)
- Batch processing
- Microservices with unpredictable traffic

**❌ Bad fit:**
- Long-running processes (> 15 min)
- High-frequency, latency-sensitive operations
- Stateful applications
- Applications requiring persistent connections (WebSockets)
- Cost-sensitive workloads with constant traffic

---

## 2. Edge Computing

### 2.1 Cloudflare Workers

**Run code at CDN edge locations worldwide**

```javascript
// worker.js
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // A/B testing at the edge
  const variant = Math.random() < 0.5 ? 'A' : 'B'

  // Rewrite path based on variant
  if (url.pathname === '/') {
    url.pathname = variant === 'A' ? '/index-a.html' : '/index-b.html'
  }

  // Fetch from origin
  const response = await fetch(url)

  // Add custom headers
  const newResponse = new Response(response.body, response)
  newResponse.headers.set('X-Variant', variant)
  newResponse.headers.set('Cache-Control', 'public, max-age=300')

  return newResponse
}
```

**Use Cases:**
- A/B testing without origin load
- Bot detection and blocking
- Authentication at edge
- API rate limiting
- Geo-routing
- Image optimization

### 2.2 Lambda@Edge (AWS CloudFront)

```javascript
// Viewer Request: Modify request before cache lookup
exports.handler = (event, context, callback) => {
    const request = event.Records[0].cf.request
    const headers = request.headers

    // Redirect mobile users
    const userAgent = headers['user-agent'][0].value
    if (/mobile/i.test(userAgent)) {
        request.uri = '/mobile' + request.uri
    }

    callback(null, request)
}

// Origin Response: Modify response from origin
exports.handler = (event, context, callback) => {
    const response = event.Records[0].cf.response
    const headers = response.headers

    // Add security headers
    headers['strict-transport-security'] = [{
        key: 'Strict-Transport-Security',
        value: 'max-age=31536000; includeSubDomains'
    }]

    callback(null, response)
}
```

---

## 3. Modern API Patterns

### 3.1 GraphQL

**Query exactly what you need**

```graphql
# Schema definition
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
}

type Query {
  user(id: ID!): User
  posts(limit: Int, offset: Int): [Post!]!
}

type Mutation {
  createPost(title: String!, content: String!): Post!
  deletePost(id: ID!): Boolean!
}
```

**Implementation (Python with Strawberry):**

```python
import strawberry
from typing import List

@strawberry.type
class User:
    id: str
    name: str
    email: str

    @strawberry.field
    def posts(self) -> List['Post']:
        return get_user_posts(self.id)

@strawberry.type
class Post:
    id: str
    title: str
    content: str

    @strawberry.field
    def author(self) -> User:
        return get_user(self.author_id)

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: str) -> User:
        return get_user(id)

    @strawberry.field
    def posts(self, limit: int = 10, offset: int = 0) -> List[Post]:
        return get_posts(limit, offset)

schema = strawberry.Schema(query=Query)
```

**GraphQL Query:**

```graphql
# Client specifies exactly what fields needed
query {
  user(id: "123") {
    name
    email
    posts {
      title
      comments {
        text
        author {
          name
        }
      }
    }
  }
}
```

**N+1 Problem and DataLoader:**

```python
from strawberry.dataloader import DataLoader

class UserDataLoader:
    async def load(self, keys: List[str]) -> List[User]:
        # Batch load all users in one query
        users = await db.query(
            "SELECT * FROM users WHERE id IN %s",
            (tuple(keys),)
        )
        # Return in same order as keys
        user_map = {u.id: u for u in users}
        return [user_map[k] for k in keys]

user_loader = DataLoader(load_fn=UserDataLoader().load)

@strawberry.field
async def author(self) -> User:
    # Batches requests automatically
    return await user_loader.load(self.author_id)
```

---

### 3.2 gRPC

**High-performance RPC framework**

```protobuf
// user.proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);
  rpc CreateUser (CreateUserRequest) returns (User);
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message GetUserRequest {
  string id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}
```

**Server Implementation (Python):**

```python
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        user = db.get_user(request.id)
        return user_pb2.User(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at
        )

    def ListUsers(self, request, context):
        # Server streaming
        users = db.list_users()
        for user in users:
            yield user_pb2.User(
                id=user.id,
                name=user.name,
                email=user.email,
                created_at=user.created_at
            )

# Start server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
server.add_insecure_port('[::]:50051')
server.start()
```

**Client:**

```python
import grpc
import user_pb2
import user_pb2_grpc

# Create channel
channel = grpc.insecure_channel('localhost:50051')
stub = user_pb2_grpc.UserServiceStub(channel)

# Unary RPC
user = stub.GetUser(user_pb2.GetUserRequest(id='123'))

# Server streaming RPC
for user in stub.ListUsers(user_pb2.ListUsersRequest()):
    print(user.name)
```

**gRPC vs REST:**

| Feature | gRPC | REST |
|---------|------|------|
| Protocol | HTTP/2 | HTTP/1.1 |
| Format | Protocol Buffers | JSON |
| Performance | Faster (binary) | Slower (text) |
| Streaming | ✅ Bidirectional | ❌ Limited |
| Browser support | ❌ Needs proxy | ✅ Native |
| Tooling | Code generation | Manual |

---

## 4. Service Mesh

### 4.1 Istio

**Manage service-to-service communication**

```yaml
# Virtual Service: Routing rules
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api
spec:
  hosts:
  - api
  http:
  # Canary deployment: 90% v1, 10% v2
  - match:
    - headers:
        user-type:
          exact: beta
    route:
    - destination:
        host: api
        subset: v2
  - route:
    - destination:
        host: api
        subset: v1
      weight: 90
    - destination:
        host: api
        subset: v2
      weight: 10

---
# Destination Rule: Load balancing, circuit breaking
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api
spec:
  host: api
  trafficPolicy:
    loadBalancer:
      simple: LEAST_REQUEST
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 60s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

**Observability (Automatic):**

```yaml
# Istio automatically provides:
- Distributed tracing (Jaeger)
- Metrics (Prometheus)
- Service graph (Kiali)
- Access logs

# No code changes required!
```

**Mutual TLS (Automatic):**

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT  # Enforce mTLS for all services
```

---

## 5. Performance Optimization

### 5.1 Database Query Optimization

**N+1 Query Problem:**

```python
# ❌ BAD: N+1 queries
users = User.query.all()  # 1 query
for user in users:
    print(user.posts)  # N queries (one per user)

# ✅ GOOD: Eager loading
from sqlalchemy.orm import joinedload

users = User.query.options(
    joinedload(User.posts)
).all()  # 1 query with JOIN
```

**Query Indexing:**

```sql
-- Slow query (full table scan)
SELECT * FROM orders WHERE user_id = 123;

-- Create index
CREATE INDEX idx_user_id ON orders(user_id);

-- Composite index for common query
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';
CREATE INDEX idx_user_status ON orders(user_id, status);

-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;
```

### 5.2 Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Configure connection pool
engine = create_engine(
    'postgresql://user:pass@db:5432/myapp',
    poolclass=QueuePool,
    pool_size=20,           # Normal connections
    max_overflow=10,        # Burst connections
    pool_timeout=30,        # Wait time for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True      # Verify connection before use
)
```

### 5.3 Caching Patterns

**Multi-Level Caching:**

```python
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory (fast, small)
        self.l2_cache = redis.Redis()  # Redis (medium, larger)

    def get(self, key):
        # Try L1 (in-memory)
        if key in self.l1_cache:
            return self.l1_cache[key]

        # Try L2 (Redis)
        value = self.l2_cache.get(key)
        if value:
            # Promote to L1
            self.l1_cache[key] = value
            return value

        # Cache miss
        return None

    def set(self, key, value, ttl=3600):
        # Set in both levels
        self.l1_cache[key] = value
        self.l2_cache.setex(key, ttl, value)
```

---

## 6. Emerging Technologies

### 6.1 WebAssembly (Wasm)

```rust
// Rust code compiled to WebAssembly
#[no_mangle]
pub extern "C" fn fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n;
    }
    fibonacci(n - 1) + fibonacci(n - 2)
}
```

**Use in Browser:**

```javascript
WebAssembly.instantiateStreaming(fetch('fibonacci.wasm'))
  .then(obj => {
    const result = obj.instance.exports.fibonacci(40)
    console.log(result)  // Much faster than JavaScript
  })
```

### 6.2 CRDTs (Conflict-Free Replicated Data Types)

**For real-time collaborative editing**

```javascript
// Y.js CRDT for collaborative text editing
import * as Y from 'yjs'

const doc = new Y.Doc()
const text = doc.getText('content')

// User 1
text.insert(0, 'Hello')

// User 2 (concurrent)
text.insert(5, ' World')

// Both users converge to: "Hello World"
// No manual conflict resolution needed!
```

### 6.3 Event Sourcing

```python
class BankAccount:
    def __init__(self, account_id):
        self.account_id = account_id
        self.balance = 0
        self.events = []

    def apply_event(self, event):
        if event['type'] == 'AccountCreated':
            self.balance = event['initial_balance']
        elif event['type'] == 'MoneyDeposited':
            self.balance += event['amount']
        elif event['type'] == 'MoneyWithdrawn':
            self.balance -= event['amount']

        self.events.append(event)

    def deposit(self, amount):
        event = {
            'type': 'MoneyDeposited',
            'amount': amount,
            'timestamp': time.time()
        }
        self.apply_event(event)
        event_store.save(self.account_id, event)

    @classmethod
    def load(cls, account_id):
        account = cls(account_id)
        events = event_store.get_events(account_id)
        for event in events:
            account.apply_event(event)
        return account
```

---

## Summary and Key Takeaways

### When to Use Each Technology

| Technology | Best For | Avoid When |
|------------|----------|------------|
| **Serverless** | Event-driven, variable traffic | Constant traffic, latency-sensitive |
| **Edge Computing** | Global latency, personalization | Complex state, heavy compute |
| **GraphQL** | Flexible client needs, mobile | Simple CRUD, caching complexity |
| **gRPC** | Microservices, high performance | Browser clients, public APIs |
| **Service Mesh** | Many microservices, security | Few services, simple deployments |
| **Event Sourcing** | Audit trails, time travel | Simple CRUD, high write volume |

### Cost vs Complexity

```
Complexity (Low → High):
REST < GraphQL < gRPC

Setup Cost (Low → High):
Serverless < Containers < VMs < Bare Metal

Operational Cost (Low → High):
Bare Metal < VMs < Containers < Serverless (at scale)
```

---

## Additional Resources

### Serverless
- AWS Lambda Documentation
- Serverless Framework
- "Serverless Architectures on AWS"

### GraphQL
- GraphQL.org
- Apollo GraphQL
- "Production Ready GraphQL"

### gRPC
- gRPC.io
- Protocol Buffers
- "gRPC Up and Running"

### Service Mesh
- Istio Documentation
- Linkerd
- "The Service Mesh Book"

### Performance
- "Designing Data-Intensive Applications"
- "High Performance Browser Networking"
- "Database Internals"
