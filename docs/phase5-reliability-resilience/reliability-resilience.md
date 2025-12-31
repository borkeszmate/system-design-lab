# Phase 5: Reliability & Resilience

## Overview

Building distributed systems that gracefully handle failures and remain operational despite component failures. This phase covers fault tolerance patterns, high availability strategies, and chaos engineering practices.

**Key Learning:** In distributed systems, failures are inevitable. The goal is not to prevent all failures, but to design systems that continue operating when failures occur.

---

## Table of Contents

1. [Fault Tolerance Patterns](#1-fault-tolerance-patterns)
2. [High Availability](#2-high-availability)
3. [Chaos Engineering](#3-chaos-engineering)

---

## 1. Fault Tolerance Patterns

### 1.1 Circuit Breaker Pattern

**Purpose:** Prevent cascading failures by stopping requests to a failing service.

**States:**
- **CLOSED:** Normal operation, requests flow through
- **OPEN:** Service is failing, requests fail immediately
- **HALF_OPEN:** Testing if service has recovered

**Implementation:**

```python
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Service unavailable."
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        return (
            time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitBreakerOpenError(Exception):
    pass


# Usage Example
def unreliable_api_call():
    response = requests.get("https://api.example.com/data", timeout=5)
    response.raise_for_status()
    return response.json()

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=requests.RequestException
)

try:
    data = circuit_breaker.call(unreliable_api_call)
except CircuitBreakerOpenError:
    # Use fallback data or cached response
    data = get_cached_data()
```

**Real-World Example - Netflix Hystrix:**

```java
@HystrixCommand(
    fallbackMethod = "getDefaultRecommendations",
    commandProperties = {
        @HystrixProperty(
            name = "circuitBreaker.requestVolumeThreshold",
            value = "10"
        ),
        @HystrixProperty(
            name = "circuitBreaker.errorThresholdPercentage",
            value = "50"
        )
    }
)
public List<Movie> getRecommendations(String userId) {
    return recommendationService.fetch(userId);
}

public List<Movie> getDefaultRecommendations(String userId) {
    // Fallback: return popular movies
    return popularMoviesCache.get();
}
```

**When to Use:**
- ✅ Calling external APIs or microservices
- ✅ Database connections that may timeout
- ✅ Any operation with potential for cascading failures
- ❌ Internal method calls in the same process

---

### 1.2 Bulkhead Pattern

**Purpose:** Isolate resources to prevent one failing component from consuming all resources.

**Analogy:** Like compartments in a ship's hull - if one compartment floods, others remain intact.

**Implementation - Thread Pool Isolation:**

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading

class Bulkhead:
    def __init__(self, max_concurrent: int, queue_size: int):
        self.semaphore = threading.Semaphore(max_concurrent)
        self.executor = ThreadPoolExecutor(
            max_workers=max_concurrent,
            thread_name_prefix="bulkhead-"
        )

    def execute(self, func, *args, timeout=30, **kwargs):
        if not self.semaphore.acquire(blocking=False):
            raise BulkheadFullError("All threads busy, request rejected")

        try:
            future = self.executor.submit(func, *args, **kwargs)
            return future.result(timeout=timeout)
        except TimeoutError:
            raise
        finally:
            self.semaphore.release()

class BulkheadFullError(Exception):
    pass


# Usage: Separate bulkheads for different services
payment_bulkhead = Bulkhead(max_concurrent=10, queue_size=50)
inventory_bulkhead = Bulkhead(max_concurrent=20, queue_size=100)
email_bulkhead = Bulkhead(max_concurrent=5, queue_size=20)

def process_order(order_id):
    # Payment service gets its own isolated resource pool
    payment_result = payment_bulkhead.execute(
        process_payment,
        order_id,
        timeout=10
    )

    # Inventory service gets a different pool
    inventory_result = inventory_bulkhead.execute(
        update_inventory,
        order_id,
        timeout=5
    )

    # Email service has smallest pool (non-critical)
    try:
        email_bulkhead.execute(send_confirmation_email, order_id)
    except BulkheadFullError:
        # Queue for later, non-critical
        email_queue.enqueue(order_id)
```

**Connection Pool Example:**

```python
# Database connection pools (using SQLAlchemy)
from sqlalchemy import create_engine

# Primary database: larger pool
primary_db = create_engine(
    'postgresql://user:pass@primary-db:5432/main',
    pool_size=20,          # Normal connections
    max_overflow=10,       # Burst connections
    pool_timeout=30,
    pool_pre_ping=True
)

# Analytics database: smaller pool (non-critical)
analytics_db = create_engine(
    'postgresql://user:pass@analytics-db:5432/analytics',
    pool_size=5,           # Limited resources
    max_overflow=2,
    pool_timeout=10
)

# If analytics queries slow down or fail,
# they won't exhaust primary database connections
```

**When to Use:**
- ✅ Isolating critical vs non-critical services
- ✅ Preventing resource exhaustion
- ✅ Multi-tenant systems (per-tenant isolation)
- ✅ Rate limiting by customer tier

---

### 1.3 Retry Pattern with Exponential Backoff

**Purpose:** Automatically retry failed operations with increasing delays.

**Formula:** `wait_time = base_delay * (2 ^ attempt) + random_jitter`

**Implementation:**

```python
import time
import random
from typing import Callable, Type

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: int = 2,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,)
):
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential calculation
        jitter: Add randomness to prevent thundering herd
        retryable_exceptions: Exceptions that should trigger retry
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except retryable_exceptions as e:
            if attempt == max_retries:
                raise  # Final attempt failed, re-raise

            # Calculate delay: base_delay * (exponential_base ^ attempt)
            delay = min(
                base_delay * (exponential_base ** attempt),
                max_delay
            )

            # Add jitter to prevent thundering herd problem
            if jitter:
                delay = delay * (0.5 + random.random())

            print(f"Attempt {attempt + 1} failed: {e}")
            print(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)


# Usage Example
def fetch_data_from_api():
    response = requests.get(
        "https://api.example.com/data",
        timeout=10
    )
    response.raise_for_status()
    return response.json()

# Retry with exponential backoff
data = retry_with_backoff(
    fetch_data_from_api,
    max_retries=5,
    base_delay=1.0,
    retryable_exceptions=(requests.RequestException,)
)
```

**Decorator Pattern:**

```python
from functools import wraps

def retry(max_retries=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise

                    delay = base_delay * (2 ** attempt)
                    delay = delay * (0.5 + random.random())
                    time.sleep(delay)
        return wrapper
    return decorator


# Usage
@retry(max_retries=3, base_delay=2.0, exceptions=(ConnectionError,))
def send_message_to_queue(message):
    return message_queue.send(message)
```

**When to Retry vs When NOT to Retry:**

```python
# ✅ DO RETRY: Transient failures
RETRYABLE_HTTP_CODES = {
    408,  # Request Timeout
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}

# ❌ DON'T RETRY: Permanent failures
NON_RETRYABLE_HTTP_CODES = {
    400,  # Bad Request
    401,  # Unauthorized
    403,  # Forbidden
    404,  # Not Found
    422,  # Unprocessable Entity
}

def should_retry(response):
    return response.status_code in RETRYABLE_HTTP_CODES
```

---

### 1.4 Timeout Management

**Purpose:** Prevent operations from blocking indefinitely.

**Timeout Hierarchy:**

```python
# 1. Request timeout (end-to-end)
REQUEST_TIMEOUT = 30.0  # Total time for entire request

# 2. Connection timeout (establishing connection)
CONNECTION_TIMEOUT = 5.0  # Time to establish connection

# 3. Read timeout (waiting for data)
READ_TIMEOUT = 10.0  # Time to receive response

# 4. Operation timeout (business logic)
OPERATION_TIMEOUT = 15.0  # Time for business operation


# Implementation with requests
import requests

response = requests.get(
    'https://api.example.com/data',
    timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
)
```

**Async Timeout Example:**

```python
import asyncio

async def fetch_user_data(user_id):
    try:
        # Timeout after 5 seconds
        async with asyncio.timeout(5.0):
            response = await client.get(f"/users/{user_id}")
            return await response.json()
    except asyncio.TimeoutError:
        logger.warning(f"Timeout fetching user {user_id}")
        return get_cached_user_data(user_id)


# Multiple operations with overall timeout
async def get_user_profile(user_id):
    try:
        async with asyncio.timeout(10.0):  # Overall timeout
            user, orders, recommendations = await asyncio.gather(
                fetch_user_data(user_id),
                fetch_user_orders(user_id),
                fetch_recommendations(user_id),
                return_exceptions=True  # Don't fail entire operation
            )

            # Handle partial failures
            return {
                'user': user if not isinstance(user, Exception) else None,
                'orders': orders if not isinstance(orders, Exception) else [],
                'recommendations': recommendations if not isinstance(recommendations, Exception) else []
            }
    except asyncio.TimeoutError:
        return get_cached_profile(user_id)
```

**Timeout Best Practices:**

```python
# ❌ BAD: No timeout (can hang forever)
response = requests.get('https://api.example.com/data')

# ❌ BAD: Same timeout for all operations
TIMEOUT = 30
db_query(timeout=TIMEOUT)        # Should be fast
external_api(timeout=TIMEOUT)    # May be slow
file_upload(timeout=TIMEOUT)     # Could be very slow

# ✅ GOOD: Specific timeouts based on expected duration
db_query(timeout=1.0)            # Database should be fast
external_api(timeout=10.0)       # API may vary
file_upload(timeout=300.0)       # Large files take time
```

---

### 1.5 Fallback Strategies

**Purpose:** Provide alternative responses when primary service fails.

**Fallback Hierarchy:**

```python
def get_product_recommendations(user_id):
    # Try 1: Personalized ML recommendations
    try:
        return ml_service.get_recommendations(user_id, timeout=2.0)
    except (TimeoutError, ServiceUnavailableError):
        pass

    # Try 2: Collaborative filtering (cached)
    try:
        return recommendation_cache.get_collaborative(user_id)
    except CacheMissError:
        pass

    # Try 3: User's purchase history
    try:
        return get_recommendations_from_history(user_id, timeout=1.0)
    except Exception:
        pass

    # Fallback 4: Popular products (always available)
    return get_popular_products()
```

**Stale Data Fallback:**

```python
import time

class CacheWithStale:
    def __init__(self, ttl=300, stale_ttl=3600):
        self.cache = {}
        self.ttl = ttl              # Fresh data timeout
        self.stale_ttl = stale_ttl  # Stale data timeout

    def get(self, key, fetch_func):
        now = time.time()

        if key in self.cache:
            value, timestamp = self.cache[key]
            age = now - timestamp

            # Return fresh data
            if age < self.ttl:
                return value

            # Try to refresh, but return stale if fetch fails
            try:
                fresh_value = fetch_func()
                self.cache[key] = (fresh_value, now)
                return fresh_value
            except Exception as e:
                # Return stale data if still within stale_ttl
                if age < self.stale_ttl:
                    logger.warning(f"Returning stale data for {key}: {e}")
                    return value
                raise

        # No cached data, must fetch
        value = fetch_func()
        self.cache[key] = (value, now)
        return value


# Usage
cache = CacheWithStale(ttl=300, stale_ttl=3600)

def get_user_profile(user_id):
    return cache.get(
        f"user:{user_id}",
        lambda: database.fetch_user(user_id)
    )
```

**Graceful Degradation:**

```python
class ProductDetailsService:
    def get_product_page(self, product_id):
        # Core data (required)
        product = self._get_product_core(product_id)

        # Enhanced data (optional, with fallbacks)
        product['reviews'] = self._get_reviews_with_fallback(product_id)
        product['recommendations'] = self._get_recommendations_with_fallback(product_id)
        product['inventory'] = self._get_inventory_with_fallback(product_id)

        return product

    def _get_reviews_with_fallback(self, product_id):
        try:
            return review_service.get_reviews(product_id, timeout=2.0)
        except Exception as e:
            logger.warning(f"Reviews unavailable: {e}")
            return {
                'count': None,
                'average_rating': None,
                'reviews': [],
                'message': 'Reviews temporarily unavailable'
            }

    def _get_recommendations_with_fallback(self, product_id):
        try:
            return recommendation_service.get_similar(product_id, timeout=2.0)
        except Exception:
            # Fallback: Return products in same category
            return self._get_category_products(product_id)

    def _get_inventory_with_fallback(self, product_id):
        try:
            return inventory_service.check_stock(product_id, timeout=1.0)
        except Exception:
            # Fallback: Assume available but show warning
            return {
                'available': True,
                'quantity': None,
                'message': 'Stock information updating'
            }
```

---

## 2. High Availability

### 2.1 Redundancy and Failover

**Active-Passive (Cold Standby):**

```yaml
# Configuration for Active-Passive setup
load_balancer:
  primary:
    host: primary.example.com
    port: 8080
    health_check:
      endpoint: /health
      interval: 5s
      timeout: 2s
      unhealthy_threshold: 3

  secondary:
    host: secondary.example.com
    port: 8080
    enabled: false  # Only activated on primary failure

  failover:
    automatic: true
    failback: manual  # Require manual intervention to fail back
```

**Active-Active (Hot Standby):**

```python
# Load balancer distributes across all active nodes
class LoadBalancer:
    def __init__(self, nodes):
        self.nodes = nodes
        self.current = 0

    def get_healthy_nodes(self):
        return [
            node for node in self.nodes
            if self.health_check(node)
        ]

    def route_request(self, request):
        healthy_nodes = self.get_healthy_nodes()

        if not healthy_nodes:
            raise NoHealthyNodesError("All nodes are down")

        # Round-robin across healthy nodes
        node = healthy_nodes[self.current % len(healthy_nodes)]
        self.current += 1

        return node.handle(request)

    def health_check(self, node):
        try:
            response = requests.get(
                f"{node.url}/health",
                timeout=2
            )
            return response.status_code == 200
        except Exception:
            return False
```

**Database Replication with Automatic Failover:**

```yaml
# PostgreSQL with Patroni for HA
patroni:
  scope: postgres-cluster
  name: postgres-1

  postgresql:
    data_dir: /var/lib/postgresql/data
    parameters:
      max_connections: 100
      shared_buffers: 256MB

  # Automatic failover configuration
  bootstrap:
    dcs:
      ttl: 30
      loop_wait: 10
      retry_timeout: 10
      maximum_lag_on_failover: 1048576  # 1MB

  watchdog:
    mode: automatic
    device: /dev/watchdog

  # Health checks
  checks:
    - name: replication_lag
      max_lag: 10  # seconds
    - name: database_size
      max_size: 100GB
```

---

### 2.2 Health Checks and Monitoring

**Levels of Health Checks:**

```python
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

# 1. Liveness Probe: Is the application running?
@app.route('/health/live')
def liveness():
    """Kubernetes uses this to know if pod should be restarted"""
    return jsonify({'status': 'alive'}), 200


# 2. Readiness Probe: Can the application serve traffic?
@app.route('/health/ready')
def readiness():
    """Kubernetes uses this to know if pod can receive traffic"""
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'disk_space': check_disk_space()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return jsonify({
        'status': 'ready' if all_healthy else 'not_ready',
        'checks': checks
    }), status_code


# 3. Startup Probe: Has the application finished starting?
@app.route('/health/startup')
def startup():
    """Kubernetes uses this for slow-starting applications"""
    checks = {
        'migrations': check_migrations_complete(),
        'cache_warmup': check_cache_warmed(),
        'connections': check_connection_pools()
    }

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return jsonify({
        'status': 'started' if all_ready else 'starting',
        'checks': checks
    }), status_code


# Dependency checks
def check_database():
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=2)
        conn.close()
        return True
    except Exception:
        return False

def check_cache():
    try:
        r = redis.Redis.from_url(REDIS_URL, socket_timeout=2)
        r.ping()
        return True
    except Exception:
        return False

def check_disk_space():
    import shutil
    stat = shutil.disk_usage('/')
    free_percent = (stat.free / stat.total) * 100
    return free_percent > 10  # At least 10% free
```

**Kubernetes Health Check Configuration:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:latest

    # Liveness: Restart if this fails
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    # Readiness: Remove from load balancer if this fails
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 2

    # Startup: Don't check liveness until this succeeds
    startupProbe:
      httpGet:
        path: /health/startup
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 30  # 30 * 5s = 150s max startup time
```

---

### 2.3 SLAs, SLOs, and SLIs

**Definitions:**
- **SLI (Service Level Indicator):** Metric that measures service performance
- **SLO (Service Level Objective):** Target value for an SLI
- **SLA (Service Level Agreement):** Contract with consequences if SLOs aren't met

**Example SLIs, SLOs, and SLAs:**

```python
# SLIs: Measurements
slis = {
    'availability': {
        'measurement': 'successful_requests / total_requests',
        'window': '30 days'
    },
    'latency': {
        'measurement': 'p95_response_time',
        'window': '5 minutes'
    },
    'error_rate': {
        'measurement': 'errors / total_requests',
        'window': '1 hour'
    },
    'throughput': {
        'measurement': 'requests_per_second',
        'window': '1 minute'
    }
}

# SLOs: Targets
slos = {
    'availability': '99.9%',      # Three nines
    'latency_p95': '200ms',       # 95th percentile
    'latency_p99': '500ms',       # 99th percentile
    'error_rate': '< 0.1%',       # Less than 0.1%
    'throughput': '> 1000 rps'    # At least 1000 req/sec
}

# SLA: Contract with customers
sla = {
    'availability': {
        'target': '99.9%',
        'measurement_period': '30 days',
        'consequences': {
            '99.0% - 99.9%': '10% credit',
            '95.0% - 99.0%': '25% credit',
            '< 95.0%': '100% credit'
        }
    }
}
```

**Calculating Downtime from Availability:**

```python
def calculate_downtime(availability_percent):
    """Calculate allowed downtime for different time periods"""
    uptime_ratio = availability_percent / 100
    downtime_ratio = 1 - uptime_ratio

    periods = {
        'year': 365.25 * 24 * 60,      # minutes
        'month': 30 * 24 * 60,
        'week': 7 * 24 * 60,
        'day': 24 * 60
    }

    results = {}
    for period_name, minutes in periods.items():
        downtime_minutes = minutes * downtime_ratio
        results[period_name] = {
            'minutes': downtime_minutes,
            'hours': downtime_minutes / 60,
            'formatted': format_duration(downtime_minutes)
        }

    return results

# Examples:
# 99.9% (Three nines)   -> 43.8 minutes/month, 8.76 hours/year
# 99.95% (Three and a half nines) -> 21.9 minutes/month, 4.38 hours/year
# 99.99% (Four nines)   -> 4.38 minutes/month, 52.56 minutes/year
# 99.999% (Five nines)  -> 26 seconds/month, 5.26 minutes/year
```

**Error Budget:**

```python
class ErrorBudget:
    def __init__(self, slo_target: float, measurement_window_days: int = 30):
        self.slo_target = slo_target  # e.g., 0.999 for 99.9%
        self.window_days = measurement_window_days
        self.error_budget = 1 - slo_target  # e.g., 0.001 for 99.9%

    def calculate_remaining_budget(self, actual_availability: float):
        """
        Calculate how much error budget remains.

        Returns:
            float: Remaining budget (0.0 to 1.0)
                  1.0 = 100% budget remaining
                  0.0 = 0% budget remaining (SLO at risk)
        """
        actual_errors = 1 - actual_availability
        budget_used = actual_errors / self.error_budget
        return max(0, 1 - budget_used)

    def can_take_risk(self, actual_availability: float, threshold: float = 0.2):
        """
        Decide if we can take risks (deploy, experiment).

        Args:
            threshold: Minimum budget required (e.g., 0.2 = keep 20% buffer)
        """
        remaining = self.calculate_remaining_budget(actual_availability)
        return remaining >= threshold


# Example usage
budget = ErrorBudget(slo_target=0.999, measurement_window_days=30)

# Current availability: 99.92%
current_availability = 0.9992
remaining = budget.calculate_remaining_budget(current_availability)

if budget.can_take_risk(current_availability):
    print("✅ Can deploy risky changes - plenty of error budget")
else:
    print("❌ Error budget low - focus on reliability")
```

---

## 3. Chaos Engineering

### 3.1 Principles of Chaos Engineering

**Goal:** Proactively discover weaknesses before they cause outages in production.

**Process:**
1. Define "steady state" (normal metrics)
2. Hypothesize that steady state continues during experiment
3. Introduce real-world failure scenarios
4. Try to disprove hypothesis by finding differences

**Starting Small:**

```python
# 1. Start in staging/test environment
# 2. Start with small experiments
# 3. Automate experiments
# 4. Gradually increase blast radius

class ChaosExperiment:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.blast_radius = "single_instance"  # Start small

    def run(self):
        # 1. Establish baseline
        baseline_metrics = self.measure_steady_state()

        # 2. Inject failure
        print(f"Injecting failure: {self.description}")
        self.inject_failure()

        # 3. Observe system behavior
        time.sleep(60)  # Observe for 1 minute
        failure_metrics = self.measure_steady_state()

        # 4. Restore normal operation
        self.restore()

        # 5. Analyze results
        return self.analyze(baseline_metrics, failure_metrics)

    def measure_steady_state(self):
        return {
            'request_success_rate': get_success_rate(),
            'avg_response_time': get_avg_response_time(),
            'error_rate': get_error_rate()
        }

    def inject_failure(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError

    def analyze(self, baseline, observed):
        degradation = {}
        for metric, baseline_value in baseline.items():
            observed_value = observed[metric]
            change_percent = (
                (observed_value - baseline_value) / baseline_value * 100
            )
            degradation[metric] = change_percent
        return degradation
```

---

### 3.2 Common Chaos Experiments

**1. Network Latency Injection:**

```python
import subprocess

class LatencyExperiment(ChaosExperiment):
    def __init__(self, target_host, delay_ms=100):
        super().__init__(
            name="network_latency",
            description=f"Add {delay_ms}ms latency to {target_host}"
        )
        self.target_host = target_host
        self.delay_ms = delay_ms

    def inject_failure(self):
        # Using Linux tc (traffic control) command
        subprocess.run([
            'tc', 'qdisc', 'add', 'dev', 'eth0',
            'root', 'netem', 'delay', f'{self.delay_ms}ms'
        ])

    def restore(self):
        subprocess.run(['tc', 'qdisc', 'del', 'dev', 'eth0', 'root'])


# Run experiment
experiment = LatencyExperiment('api.example.com', delay_ms=200)
results = experiment.run()
```

**2. Service Unavailability:**

```python
class ServiceDownExperiment(ChaosExperiment):
    def __init__(self, service_name):
        super().__init__(
            name="service_down",
            description=f"Stop {service_name} service"
        )
        self.service_name = service_name

    def inject_failure(self):
        # Stop a service instance
        subprocess.run(['systemctl', 'stop', self.service_name])

    def restore(self):
        subprocess.run(['systemctl', 'start', self.service_name])
```

**3. Resource Exhaustion:**

```python
class CPUStressExperiment(ChaosExperiment):
    def __init__(self, cpu_percent=80, duration=60):
        super().__init__(
            name="cpu_stress",
            description=f"Consume {cpu_percent}% CPU for {duration}s"
        )
        self.cpu_percent = cpu_percent
        self.duration = duration
        self.process = None

    def inject_failure(self):
        # Using stress-ng tool
        self.process = subprocess.Popen([
            'stress-ng',
            '--cpu', '4',
            '--cpu-load', str(self.cpu_percent),
            '--timeout', f'{self.duration}s'
        ])

    def restore(self):
        if self.process:
            self.process.terminate()
```

**4. Database Connection Failure:**

```python
class DatabaseChaosExperiment(ChaosExperiment):
    def inject_failure(self):
        # Block database port using iptables
        subprocess.run([
            'iptables', '-A', 'OUTPUT',
            '-p', 'tcp', '--dport', '5432',
            '-j', 'DROP'
        ])

    def restore(self):
        subprocess.run([
            'iptables', '-D', 'OUTPUT',
            '-p', 'tcp', '--dport', '5432',
            '-j', 'DROP'
        ])
```

---

### 3.3 Chaos Tools

**Chaos Monkey (Netflix):**

```yaml
# Chaos Monkey configuration
chaosmonkey:
  enabled: true
  schedule:
    enabled: true
    frequency: daily
    hour: 10  # 10 AM

  termination:
    # Only terminate instances in Auto Scaling Groups
    asg_only: true

    # Probability of terminating an instance
    probability: 0.1  # 10% chance per day

    # Groups to target
    opt_in:
      - production-web-servers
      - production-api-servers

    # Groups to exclude
    opt_out:
      - production-databases
      - production-cache
```

**Gremlin (Failure as a Service):**

```python
import gremlin

# CPU attack
gremlin.attack.cpu(
    length=60,           # Duration in seconds
    cores=2,             # Number of CPU cores to stress
    percent=75,          # CPU utilization percentage
    target={
        'type': 'Random',
        'percent': 10    # Target 10% of instances
    }
)

# Network attack - latency
gremlin.attack.latency(
    length=300,
    delay=100,           # Milliseconds of latency
    target={
        'type': 'Container',
        'labels': {'service': 'api'}
    }
)

# Network attack - packet loss
gremlin.attack.packet_loss(
    length=120,
    percent=10,          # 10% packet loss
    target={
        'type': 'Host',
        'tags': {'env': 'staging'}
    }
)
```

**Chaos Mesh (Kubernetes):**

```yaml
# Network chaos - add latency
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
spec:
  action: delay
  mode: one
  selector:
    namespaces:
      - production
    labelSelectors:
      app: web
  delay:
    latency: "100ms"
    correlation: "100"
    jitter: "0ms"
  duration: "5m"

---

# Pod chaos - kill pods
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-failure
spec:
  action: pod-kill
  mode: fixed
  value: "1"  # Kill 1 pod
  selector:
    namespaces:
      - production
    labelSelectors:
      app: api
  scheduler:
    cron: "@every 2h"

---

# Stress chaos - CPU stress
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: cpu-stress
spec:
  mode: one
  selector:
    labelSelectors:
      app: worker
  stressors:
    cpu:
      workers: 2
      load: 80
  duration: "10m"
```

---

### 3.4 GameDay Exercises

**Planning a GameDay:**

```markdown
# GameDay Exercise: Database Failover

## Objective
Verify that our application can survive a primary database failure
and automatically failover to the replica.

## Participants
- Backend team
- SRE team
- Product manager (observer)

## Prerequisites
- [ ] All monitoring dashboards operational
- [ ] Incident response channel ready (#incident-response)
- [ ] Rollback plan documented and reviewed
- [ ] Customer support team notified

## Scenario
At 10:00 AM, we will simulate a primary database failure by:
1. Stopping the primary PostgreSQL instance
2. Observing automatic failover to replica
3. Verifying application continues serving traffic

## Success Criteria
- Application remains available (> 99% success rate)
- Failover completes within 30 seconds
- No data loss
- All alerts fire correctly

## Timeline
- 09:45 - Team assembles, final check
- 10:00 - Inject failure (stop primary database)
- 10:00-10:05 - Observe system behavior
- 10:05 - Restore normal operation
- 10:05-10:30 - Debrief and document learnings

## Observations
[Document what happens during the exercise]

## Learnings
[Document what we learned and action items]
```

---

## Hands-On Exercises

### Exercise 1: Implement Circuit Breaker

Build a service that calls an unreliable API with circuit breaker protection:

```python
# TODO: Implement circuit breaker for this function
def fetch_weather_data(city):
    response = requests.get(f"https://api.weather.com/{city}")
    return response.json()

# Requirements:
# - Open circuit after 5 consecutive failures
# - Wait 60 seconds before attempting to close
# - Provide fallback weather data when circuit is open
```

### Exercise 2: Set Up Health Checks

Create a Flask/FastAPI application with proper health check endpoints:

```python
# TODO: Implement health checks
# - /health/live - Basic liveness check
# - /health/ready - Check database and cache connectivity
# - /health/startup - Verify migrations and cache warmup
```

### Exercise 3: Calculate Error Budget

```python
# Given SLO: 99.9% availability over 30 days
# Current availability: 99.85%
# Question: How much error budget remains?
# Can we proceed with a risky deployment?
```

### Exercise 4: Run a Chaos Experiment

```bash
# Use Chaos Mesh to inject 100ms network latency
# to your application for 5 minutes
# Measure the impact on user experience
```

---

## Summary and Key Takeaways

### Reliability Patterns
- **Circuit Breaker:** Stop calling failing services
- **Bulkhead:** Isolate resources to prevent cascading failures
- **Retry:** Handle transient failures automatically
- **Timeout:** Don't wait forever
- **Fallback:** Always have a Plan B

### High Availability
- **Redundancy:** Multiple instances of critical components
- **Health Checks:** Know when components fail
- **SLOs:** Measure what matters to users
- **Error Budget:** Balance innovation and reliability

### Chaos Engineering
- **Proactive testing:** Find weaknesses before users do
- **Start small:** Single instance → multiple instances → production
- **Automate:** Make chaos experiments repeatable
- **Learn:** Turn failures into improvements

### Key Metrics
- **Availability:** % of time system is operational
- **MTBF:** Mean Time Between Failures
- **MTTR:** Mean Time To Recovery (minimize this!)
- **Error Rate:** % of failed requests

---

## Additional Resources

### Books
- "Release It!" by Michael Nygard
- "Site Reliability Engineering" by Google
- "Chaos Engineering" by Netflix Engineers

### Tools
- **Circuit Breakers:** Hystrix, Resilience4j, Polly
- **Chaos Engineering:** Chaos Monkey, Gremlin, Chaos Mesh, Litmus
- **Load Testing:** Locust, k6, Gatling
- **Observability:** Prometheus, Grafana, Datadog

### Articles
- Netflix Tech Blog: Chaos Engineering
- Google SRE Book: Embracing Risk
- AWS Well-Architected: Reliability Pillar
