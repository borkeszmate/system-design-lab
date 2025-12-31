# Phase 6: Observability & Monitoring

## Overview

Observability is the ability to understand what's happening inside a system by examining its outputs. In distributed systems, observability is critical for debugging, performance optimization, and maintaining reliability.

**Key Insight:** You can't fix what you can't see. Observability turns unknown-unknowns into known-unknowns.

---

## Table of Contents

1. [The Three Pillars of Observability](#1-the-three-pillars-of-observability)
2. [Metrics and Monitoring](#2-metrics-and-monitoring)
3. [Logging](#3-logging)
4. [Distributed Tracing](#4-distributed-tracing)
5. [Alerting and On-Call](#5-alerting-and-on-call)

---

## 1. The Three Pillars of Observability

### 1.1 Overview

**Metrics:** Numerical measurements aggregated over time
- "What is the 95th percentile response time?"
- "How many requests per second?"

**Logs:** Discrete events with context
- "What happened at 10:15:32 when user X tried to checkout?"
- "What was the error message?"

**Traces:** Request flow through distributed system
- "Which services did this request touch?"
- "Where did it spend the most time?"

**Visualization:**

```
Request Journey (Distributed Trace):
Client → API Gateway → Auth Service → Order Service → Payment Service → Database
  |         |              |              |               |                |
 10ms      5ms           15ms           50ms          200ms            100ms
                                                       ^^^^
                                                    SLOW! Investigate

Metrics:
- Request rate: 1000 rps
- Error rate: 0.5%
- p95 latency: 250ms

Logs from Payment Service:
[ERROR] Payment gateway timeout: connection_timeout after 30s
```

---

## 2. Metrics and Monitoring

### 2.1 Types of Metrics

**Counters:** Only increase (or reset)
```python
# Examples:
total_requests = 10542
total_errors = 23
total_users_registered = 1523

# Prometheus counter
from prometheus_client import Counter

request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_counter.labels(
    method='GET',
    endpoint='/api/users',
    status='200'
).inc()
```

**Gauges:** Can go up or down
```python
# Examples:
current_active_users = 523
memory_usage_bytes = 1024000000
queue_depth = 42

# Prometheus gauge
from prometheus_client import Gauge

active_users = Gauge(
    'active_users',
    'Number of currently active users'
)

active_users.set(523)
active_users.inc()  # 524
active_users.dec(5)  # 519
```

**Histograms:** Distribution of values
```python
# Track response time distribution
from prometheus_client import Histogram

response_time = Histogram(
    'http_response_time_seconds',
    'HTTP response time',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

# Record observation
with response_time.labels(endpoint='/api/orders').time():
    process_order()

# Prometheus automatically calculates:
# - Count of observations
# - Sum of all observed values
# - Histogram buckets
# - Quantiles (p50, p95, p99)
```

**Summaries:** Similar to histograms, pre-calculated quantiles
```python
from prometheus_client import Summary

request_latency = Summary(
    'request_latency_seconds',
    'Request latency in seconds',
    ['service']
)

request_latency.labels(service='api').observe(0.152)
```

---

### 2.2 The RED Method (for Services)

**R**equests: Rate of requests
**E**rrors: Rate of failed requests
**D**uration: Distribution of request durations

```python
from prometheus_client import Counter, Histogram
import time
from functools import wraps

# Requests
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Errors (subset of requests_total with status >= 400)
http_request_errors_total = Counter(
    'http_request_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status']
)


# Decorator to automatically track RED metrics
def track_red_metrics(method, endpoint):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                status = getattr(result, 'status_code', 200)

                # Track request
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()

                # Track errors (4xx, 5xx)
                if status >= 400:
                    http_request_errors_total.labels(
                        method=method,
                        endpoint=endpoint,
                        status=status
                    ).inc()

                return result

            finally:
                # Track duration
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

        return wrapper
    return decorator


# Usage
@track_red_metrics('GET', '/api/users')
def get_users():
    return fetch_users_from_db()
```

---

### 2.3 The USE Method (for Resources)

**U**tilization: % of time resource is busy
**S**aturation: Amount of queued work
**E**rrors: Count of errors

```python
from prometheus_client import Gauge

# CPU
cpu_utilization = Gauge('cpu_utilization_percent', 'CPU utilization')
cpu_utilization.set(75.5)

# Memory
memory_utilization = Gauge('memory_utilization_percent', 'Memory utilization')
memory_saturation = Gauge('memory_swap_usage_bytes', 'Swap usage')

# Disk
disk_utilization = Gauge('disk_utilization_percent', 'Disk utilization')
disk_saturation = Gauge('disk_io_queue_depth', 'Disk I/O queue depth')

# Network
network_utilization = Gauge('network_utilization_percent', 'Network utilization')
network_saturation = Gauge('network_retransmit_rate', 'TCP retransmit rate')
```

---

### 2.4 Golden Signals (Google SRE)

**Latency:** Time to service a request
**Traffic:** Demand on the system
**Errors:** Rate of failed requests
**Saturation:** How "full" the service is

```python
# Complete example with all golden signals
from prometheus_client import Counter, Histogram, Gauge

class GoldenSignals:
    def __init__(self, service_name):
        # Latency
        self.latency = Histogram(
            f'{service_name}_request_duration_seconds',
            'Request duration',
            ['endpoint'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0]
        )

        # Traffic
        self.traffic = Counter(
            f'{service_name}_requests_total',
            'Total requests',
            ['endpoint']
        )

        # Errors
        self.errors = Counter(
            f'{service_name}_errors_total',
            'Total errors',
            ['endpoint', 'error_type']
        )

        # Saturation
        self.saturation = Gauge(
            f'{service_name}_saturation',
            'Service saturation (0-1)',
            ['resource']
        )

    def record_request(self, endpoint, duration, error=None):
        # Record traffic
        self.traffic.labels(endpoint=endpoint).inc()

        # Record latency
        self.latency.labels(endpoint=endpoint).observe(duration)

        # Record error if present
        if error:
            self.errors.labels(
                endpoint=endpoint,
                error_type=type(error).__name__
            ).inc()

    def update_saturation(self, resource, value):
        """
        Update saturation (0.0 to 1.0)
        Examples:
        - CPU: current_usage / total_capacity
        - Memory: used_memory / total_memory
        - Connections: active_connections / max_connections
        """
        self.saturation.labels(resource=resource).set(value)


# Usage
signals = GoldenSignals('order_service')

def process_order(order_id):
    start = time.time()
    error = None

    try:
        # Process order
        result = do_processing(order_id)
        return result
    except Exception as e:
        error = e
        raise
    finally:
        duration = time.time() - start
        signals.record_request('/orders', duration, error)

# Update saturation periodically
def update_saturation_metrics():
    import psutil

    # CPU saturation
    cpu_percent = psutil.cpu_percent() / 100
    signals.update_saturation('cpu', cpu_percent)

    # Memory saturation
    memory = psutil.virtual_memory()
    memory_percent = memory.percent / 100
    signals.update_saturation('memory', memory_percent)

    # Connection pool saturation
    active_connections = db_pool.active_count()
    max_connections = db_pool.max_size
    connection_saturation = active_connections / max_connections
    signals.update_saturation('db_connections', connection_saturation)
```

---

### 2.5 Prometheus and Grafana

**Prometheus Setup:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Application services
  - job_name: 'api-service'
    static_configs:
      - targets: ['api:8080']
    metrics_path: '/metrics'

  # Service discovery (Kubernetes)
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
```

**PromQL Queries:**

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate (percentage)
rate(http_request_errors_total[5m]) / rate(http_requests_total[5m]) * 100

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# p99 latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# CPU usage by pod
avg by (pod) (rate(container_cpu_usage_seconds_total[5m]))

# Memory usage
container_memory_usage_bytes / container_memory_limit_bytes * 100

# Disk usage
(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100

# Predict when disk will be full (linear regression)
predict_linear(node_filesystem_free_bytes[1h], 4 * 3600) < 0
```

**Grafana Dashboard (JSON):**

```json
{
  "dashboard": {
    "title": "API Service Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{service=\"api\"}[5m])",
            "legendFormat": "{{endpoint}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_request_errors_total[5m]) / rate(http_requests_total[5m]) * 100"
          }
        ],
        "type": "graph",
        "alert": {
          "conditions": [
            {
              "evaluator": {
                "params": [5],
                "type": "gt"
              },
              "query": {
                "params": ["A", "5m", "now"]
              }
            }
          ]
        }
      },
      {
        "title": "Latency (p95, p99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

---

## 3. Logging

### 3.1 Structured Logging

**Bad: Unstructured logs**
```python
# ❌ Hard to parse and search
print("User john logged in")
print("Error processing order 12345: payment failed")
```

**Good: Structured logs (JSON)**
```python
import json
import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

    def log(self, level, message, **context):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'service': self.service_name,
            'message': message,
            **context
        }
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )

    def info(self, message, **context):
        self.log('info', message, **context)

    def error(self, message, **context):
        self.log('error', message, **context)

    def warning(self, message, **context):
        self.log('warning', message, **context)


# Usage
logger = StructuredLogger('order-service')

logger.info(
    'User logged in',
    user_id='123',
    username='john',
    ip_address='192.168.1.1'
)
# Output: {"timestamp": "2024-01-15T10:30:45.123Z", "level": "info", "service": "order-service", "message": "User logged in", "user_id": "123", "username": "john", "ip_address": "192.168.1.1"}

logger.error(
    'Payment failed',
    order_id='12345',
    user_id='123',
    error_code='GATEWAY_TIMEOUT',
    amount=99.99
)
```

---

### 3.2 Log Levels

```python
# Standard log levels (in order of severity)
LEVELS = {
    'DEBUG': 10,     # Detailed information for diagnosing problems
    'INFO': 20,      # General informational messages
    'WARNING': 30,   # Warning messages (non-critical issues)
    'ERROR': 40,     # Error messages (operation failed)
    'CRITICAL': 50   # Critical issues (system unstable)
}

# Usage guidelines
logger.debug(
    'Database query executed',
    query='SELECT * FROM users WHERE id = ?',
    params=[123],
    duration_ms=15
)  # Only in development

logger.info(
    'Order created',
    order_id='ORD-123',
    user_id='USR-456',
    total=99.99
)  # Business events

logger.warning(
    'High memory usage detected',
    memory_percent=85,
    threshold=80
)  # Potential issues

logger.error(
    'Failed to send email',
    user_id='USR-789',
    email='user@example.com',
    error='SMTP connection timeout'
)  # Operation failures

logger.critical(
    'Database connection pool exhausted',
    active_connections=100,
    max_connections=100
)  # System-level issues
```

---

### 3.3 Correlation IDs

**Purpose:** Track a request across multiple services

```python
import uuid
from contextvars import ContextVar

# Context variable to store request ID
request_id_var = ContextVar('request_id', default=None)

class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Extract or generate request ID
        request_id = (
            environ.get('HTTP_X_REQUEST_ID') or
            str(uuid.uuid4())
        )

        # Store in context
        request_id_var.set(request_id)

        # Add to response headers
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('X-Request-ID', request_id))
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)


# Enhanced logger that includes request ID
class ContextLogger(StructuredLogger):
    def log(self, level, message, **context):
        request_id = request_id_var.get()
        if request_id:
            context['request_id'] = request_id

        # Also get trace ID if using distributed tracing
        trace_id = get_current_trace_id()  # From tracing library
        if trace_id:
            context['trace_id'] = trace_id

        super().log(level, message, **context)


# Usage across services
# Service 1: API Gateway
logger.info('Received order request', user_id='123')

# Service 2: Order Service (propagate request_id)
def call_payment_service(order_data):
    headers = {
        'X-Request-ID': request_id_var.get(),
        'Content-Type': 'application/json'
    }
    response = requests.post(
        'http://payment-service/process',
        json=order_data,
        headers=headers
    )
    return response

# Service 3: Payment Service
logger.info('Processing payment', order_id='456', amount=99.99)

# All logs will have same request_id, allowing you to trace entire request flow
```

---

### 3.4 ELK Stack (Elasticsearch, Logstash, Kibana)

**Logstash Pipeline:**

```ruby
# logstash.conf
input {
  # Read from files
  file {
    path => "/var/log/app/*.log"
    start_position => "beginning"
    codec => json
  }

  # Read from TCP
  tcp {
    port => 5000
    codec => json_lines
  }
}

filter {
  # Parse timestamp
  date {
    match => ["timestamp", "ISO8601"]
    target => "@timestamp"
  }

  # Add geo-location for IP addresses
  geoip {
    source => "ip_address"
  }

  # Parse user agent
  useragent {
    source => "user_agent"
    target => "user_agent_parsed"
  }

  # Extract error stack traces
  if [level] == "error" {
    mutate {
      add_tag => ["error"]
    }
  }
}

output {
  # Send to Elasticsearch
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{[service]}-%{+YYYY.MM.dd}"
  }

  # Also print to stdout for debugging
  stdout {
    codec => rubydebug
  }
}
```

**Elasticsearch Query:**

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "service": "order-service"
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-1h"
            }
          }
        }
      ],
      "filter": [
        {
          "term": {
            "level": "error"
          }
        }
      ]
    }
  },
  "aggs": {
    "errors_by_type": {
      "terms": {
        "field": "error_type.keyword"
      }
    }
  }
}
```

---

## 4. Distributed Tracing

### 4.1 OpenTelemetry

**Instrumentation:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Set up tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure exporter (Jaeger)
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# Add span processor
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Auto-instrument libraries
RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)


# Manual instrumentation
def process_order(order_id):
    # Create a span
    with tracer.start_as_current_span("process_order") as span:
        # Add attributes
        span.set_attribute("order_id", order_id)
        span.set_attribute("user_id", get_user_id())

        # Child span for database operation
        with tracer.start_as_current_span("fetch_order_details"):
            order = db.query(f"SELECT * FROM orders WHERE id = {order_id}")

        # Child span for external API call
        with tracer.start_as_current_span("verify_payment") as payment_span:
            payment_span.set_attribute("payment_gateway", "stripe")
            result = payment_service.verify(order)

            if not result.success:
                # Record error in span
                payment_span.set_status(
                    trace.Status(trace.StatusCode.ERROR, "Payment verification failed")
                )
                payment_span.record_exception(result.error)

        return order
```

**Trace Context Propagation:**

```python
# Service A (Order Service)
import requests
from opentelemetry import trace
from opentelemetry.propagate import inject

def call_payment_service(order_data):
    headers = {}

    # Inject trace context into headers
    inject(headers)

    # Headers now contain: traceparent, tracestate
    response = requests.post(
        'http://payment-service/process',
        json=order_data,
        headers=headers
    )
    return response


# Service B (Payment Service)
from opentelemetry.propagate import extract
from flask import Flask, request

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_payment():
    # Extract trace context from headers
    context = extract(request.headers)

    # Continue the trace
    with tracer.start_as_current_span("process_payment", context=context):
        # This span will be a child of the span from Service A
        result = charge_payment(request.json)
        return result
```

---

### 4.2 Trace Visualization

**Example Trace:**

```
Request: POST /api/orders
Total Duration: 325ms

├─ [API Gateway] handle_request (325ms)
│  ├─ [Auth Service] verify_token (15ms)
│  ├─ [Order Service] create_order (290ms)
│  │  ├─ [Database] insert_order (20ms)
│  │  ├─ [Inventory Service] check_stock (50ms)
│  │  │  └─ [Database] query_inventory (45ms)
│  │  ├─ [Payment Service] process_payment (200ms) ⚠️ SLOW
│  │  │  ├─ [Database] get_payment_method (10ms)
│  │  │  ├─ [External API] charge_card (180ms) 🔴 BOTTLENECK
│  │  │  └─ [Database] save_transaction (10ms)
│  │  └─ [Notification Service] send_confirmation (20ms)
│  │     └─ [Email Service] send_email (18ms)
│  └─ [Response] serialize_response (5ms)
```

**Jaeger Query:**

```python
# Find slow traces (> 500ms)
{
  "service": "order-service",
  "operation": "create_order",
  "tags": {
    "http.status_code": "200"
  },
  "minDuration": "500ms"
}

# Find traces with errors
{
  "service": "payment-service",
  "tags": {
    "error": "true"
  }
}
```

---

### 4.3 Sampling Strategies

**Problem:** Tracing every request is expensive at scale.

**Solution:** Sample a percentage of requests.

```python
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    ALWAYS_ON,
    ALWAYS_OFF
)

# 1. Sample 10% of all requests
sampler = TraceIdRatioBased(0.1)

# 2. Always sample if parent is sampled
sampler = ParentBased(root=TraceIdRatioBased(0.1))

# 3. Always sample errors, 10% of successful requests
class ErrorAwareSampler:
    def __init__(self, success_rate=0.1):
        self.success_rate = success_rate
        self.success_sampler = TraceIdRatioBased(success_rate)
        self.error_sampler = ALWAYS_ON

    def should_sample(self, context, trace_id, name, attributes=None, **kwargs):
        # Always sample if error
        if attributes and attributes.get('error'):
            return self.error_sampler.should_sample(
                context, trace_id, name, attributes, **kwargs
            )

        # Otherwise use ratio-based sampling
        return self.success_sampler.should_sample(
            context, trace_id, name, attributes, **kwargs
        )


# 4. Sample 100% of slow requests, 1% of fast requests
class LatencyAwareSampler:
    def __init__(self, latency_threshold_ms=1000, slow_sample_rate=1.0, fast_sample_rate=0.01):
        self.latency_threshold = latency_threshold_ms / 1000
        self.slow_sampler = TraceIdRatioBased(slow_sample_rate)
        self.fast_sampler = TraceIdRatioBased(fast_sample_rate)

    def should_sample(self, context, trace_id, name, attributes=None, **kwargs):
        if attributes and attributes.get('duration_ms', 0) > self.latency_threshold:
            return self.slow_sampler.should_sample(
                context, trace_id, name, attributes, **kwargs
            )
        return self.fast_sampler.should_sample(
            context, trace_id, name, attributes, **kwargs
        )
```

---

## 5. Alerting and On-Call

### 5.1 Alert Design Principles

**Good alerts are:**
1. **Actionable:** Receiver can fix the problem
2. **Relevant:** Actually indicates a problem
3. **Timely:** Fires before users are impacted
4. **Specific:** Clear what's wrong and where

**Bad Alert Examples:**

```yaml
# ❌ TOO NOISY
alert: HighCPU
expr: cpu_usage > 50
# Fires constantly, becomes ignored

# ❌ NOT ACTIONABLE
alert: SomethingWrong
expr: error_rate > 0
description: "There are errors"
# What errors? Where? What should I do?

# ❌ TOO LATE
alert: DiskFull
expr: disk_usage > 95
# Should alert at 80% to give time to act
```

**Good Alert Examples:**

```yaml
# ✅ GOOD: Actionable, specific, timely
alert: HighErrorRate
expr: |
  rate(http_request_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
for: 5m
labels:
  severity: critical
  service: api
annotations:
  summary: "API error rate above 5% for 5 minutes"
  description: |
    Current error rate: {{ $value | humanizePercentage }}
    Runbook: https://wiki.company.com/runbooks/high-error-rate
  dashboard: https://grafana.company.com/d/api-overview

# ✅ GOOD: Predictive, gives time to act
alert: DiskSpaceFillingUp
expr: |
  predict_linear(node_filesystem_free_bytes[1h], 4 * 3600) < 0
for: 10m
labels:
  severity: warning
annotations:
  summary: "Disk will be full in 4 hours"
  description: |
    Current usage: {{ $value | humanize }}
    Projected full: 4 hours
    Action: Clean up logs or expand disk

# ✅ GOOD: Latency alert based on SLO
alert: HighLatency
expr: |
  histogram_quantile(0.95,
    rate(http_request_duration_seconds_bucket[5m])
  ) > 0.5
for: 10m
labels:
  severity: warning
annotations:
  summary: "p95 latency above SLO (500ms)"
  description: |
    Current p95: {{ $value | humanizeDuration }}
    SLO: 500ms
```

---

### 5.2 Alert Fatigue Prevention

**Strategies:**

1. **Use `for` clause to avoid flapping:**
```yaml
# Only fire after 5 minutes of sustained violation
for: 5m
```

2. **Group related alerts:**
```yaml
# Instead of alerting on each instance, alert on service
expr: |
  sum by (service) (up) / count by (service) (up) < 0.5
annotations:
  summary: "More than 50% of {{ $labels.service }} instances are down"
```

3. **Alert on symptoms, not causes:**
```yaml
# ❌ Alert on disk usage (cause)
alert: HighDiskUsage
expr: disk_usage > 80

# ✅ Alert on slow queries (symptom)
alert: SlowDatabaseQueries
expr: mysql_query_duration_p95 > 1.0
```

4. **Use severity levels:**
```yaml
# warning: Page during business hours
# critical: Page immediately
labels:
  severity: warning  # or critical
```

---

### 5.3 On-Call Best Practices

**Runbooks:**

```markdown
# Runbook: High API Error Rate

## Symptoms
- Error rate > 5% for 5+ minutes
- Users reporting failed requests
- Alert: HighErrorRate firing

## Impact
- Users cannot complete orders
- Revenue impact: ~$1000/minute

## Diagnosis
1. Check Grafana dashboard: https://grafana.company.com/d/api-overview
2. Check recent deployments: `kubectl rollout history deployment/api`
3. Check error logs:
   ```
   kubectl logs -l app=api --tail=100 | grep ERROR
   ```
4. Check external dependencies:
   - Payment gateway status: https://status.stripe.com
   - Database health: Check `db-health` dashboard

## Resolution

### If recent deployment:
```bash
kubectl rollout undo deployment/api
```

### If payment gateway down:
Enable fallback mode:
```bash
kubectl set env deployment/api PAYMENT_FALLBACK_MODE=true
```

### If database issues:
1. Check slow query log
2. Consider killing long-running queries
3. Escalate to DBA if needed

## Prevention
- Add integration tests for error scenarios
- Implement circuit breaker for payment gateway
- Add database query timeout

## Escalation
If unable to resolve in 15 minutes:
- Escalate to: @senior-engineer
- Notify: #incidents channel
- Update status page: https://status.company.com
```

---

### 5.4 Incident Response

**Incident Severity Levels:**

```python
SEVERITY = {
    'SEV1': {
        'description': 'Critical customer impact',
        'examples': ['Site down', 'Data breach', 'Payment processing down'],
        'response_time': '5 minutes',
        'communication': 'Hourly updates to leadership',
        'status_page': 'Required'
    },
    'SEV2': {
        'description': 'Significant customer impact',
        'examples': ['Slow response times', 'Feature unavailable'],
        'response_time': '15 minutes',
        'communication': 'Updates every 2 hours',
        'status_page': 'Recommended'
    },
    'SEV3': {
        'description': 'Minor customer impact',
        'examples': ['Non-critical feature broken', 'Degraded performance'],
        'response_time': '1 hour',
        'communication': 'Daily summary',
        'status_page': 'Optional'
    }
}
```

**Incident Timeline:**

```
T+0:00  - Alert fires
T+0:05  - On-call engineer acknowledges
T+0:10  - Initial diagnosis complete
T+0:15  - Incident declared (SEV2)
T+0:20  - Mitigation started (rollback deployment)
T+0:25  - Service restored
T+1:00  - Monitoring for stability
T+2:00  - Incident resolved
T+24:00 - Post-mortem scheduled
T+72:00 - Post-mortem completed
```

---

## Summary and Key Takeaways

### Three Pillars
- **Metrics:** What is happening (aggregated numbers)
- **Logs:** Why it's happening (detailed events)
- **Traces:** Where time is spent (request flow)

### Metrics Best Practices
- Use RED method for services (Requests, Errors, Duration)
- Use USE method for resources (Utilization, Saturation, Errors)
- Track Golden Signals (Latency, Traffic, Errors, Saturation)
- Use histograms for latency, counters for totals

### Logging Best Practices
- Always use structured logging (JSON)
- Include correlation IDs for request tracking
- Use appropriate log levels
- Don't log sensitive data (passwords, tokens)

### Tracing Best Practices
- Use OpenTelemetry for vendor-neutral instrumentation
- Propagate context across service boundaries
- Use sampling to reduce overhead
- Always trace errors, sample successes

### Alerting Best Practices
- Make alerts actionable
- Avoid alert fatigue (use `for` clause)
- Include runbook links
- Alert on symptoms, not causes

---

## Additional Resources

### Tools
- **Metrics:** Prometheus, Grafana, Datadog, New Relic
- **Logging:** ELK Stack, Loki, Splunk
- **Tracing:** Jaeger, Zipkin, Lightstep
- **All-in-One:** Datadog, New Relic, Honeycomb

### Books
- "Observability Engineering" by Charity Majors
- "Site Reliability Engineering" (Google)
- "Distributed Systems Observability" by Cindy Sridharan

### Standards
- OpenTelemetry: https://opentelemetry.io
- OpenMetrics: https://openmetrics.io
